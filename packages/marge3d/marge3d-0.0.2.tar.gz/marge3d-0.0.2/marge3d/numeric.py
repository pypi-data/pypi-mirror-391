"""
TODO : documentation ...
"""
import numpy as np
import scipy.sparse as sp

from marge3d.params import DaitcheParameters

class NumericalSolver:

    def __init__(self, x, w, velocity_field, Nt, order, particle_density, fluid_density, particle_radius,
                       kinematic_viscosity, time_scale, char_vel):

        self.w       = np.copy(w)       # velocity difference
        self.x       = np.copy(x)       # particle position
        self.p       = DaitcheParameters(particle_density, fluid_density,
                            particle_radius, kinematic_viscosity, time_scale, char_vel)


        self.vel     = velocity_field

        '''
        if self.vel.limits == True:
            if (x[0] > self.vel.x_right or x[0] < self.vel.x_left or x[1] > self.vel.y_up or x[1] < self.vel.y_down):
                  raise Exception("Particle's initial position is outside the spatial domain")
        '''

        if order == 1:
            self.calc_alpha_mat(Nt)
        elif order == 2:
            self.euler_nodes  = 151 # This number could be increased to increase accuracy
            self.calc_alpha_mat(self.euler_nodes)
            self.calc_beta_mat(Nt)
        elif order == 3:
            self.euler_nodes  = 151 # This number could be increased to increase accuracy
            self.calc_alpha_mat(self.euler_nodes)
            self.calc_beta_mat(self.euler_nodes)
            self.calc_gamma_mat(Nt)
        else:
            raise("Requested order for Daitche's method not available.")


    def calculate_G(self, w1, w2, w3, x, y, z, t):

        coeff              = self.p.R - 1.0

        #u1, u2, u3         = self.vel.get_velocity(x, y, z, t)
        u1, u2, u3         = self.vel.get_velocity(x, y, z, t)

        u1x, u1y, u1z, u2x, u2y, u2z, u3x, u3y, u3z  = self.vel.get_gradient(x, y, z, t)

        u1t, u2t, u3t      = self.vel.get_dudt(x, y, z, t)

        G1                 = coeff * u1t + (coeff * u1 - w1) * u1x + \
                                      (coeff * u2 - w2) * u1y + \
                                        (coeff * u3 - w3) * u1z

        G2                 = coeff * u2t + (coeff * u1 - w1) * u2x + \
                                      (coeff * u2 - w2) * u2y  + \
                                        (coeff * u3 - w3) * u2z

        G3                 = coeff * u3t + (coeff * u1 - w1) * u3x + \
                                       (coeff * u2 - w2) * u3y  + \
                                         (coeff * u3 - w3) * u3z
        return G1, G2, G3



    def alpha_jn(self, j, n):
        if n == 0:
            return 0.0
        elif j == 0:
            return 4.0 / 3.0
        elif j != n:
            return ((j - 1.0)**1.5 + (j + 1.0)**1.5 - 2.0 * j**1.5) * 4.0 / 3.0
        else:
            return ((n - 1.0)**1.5 - n**1.5 + np.sqrt(n)*3.0/2.0) * 4.0/3.0



    def alpha_v(self, N):

        AlphaSubst_v = np.array([])
        for j in range(0, N+1):
            AlphaSubst_v = np.append(AlphaSubst_v,
                              self.alpha_jn(j+1, N+1) -\
                                  self.alpha_jn(j, N))

        return AlphaSubst_v


    def calc_alpha_mat(self, N):
        for nn in range(0, N-1):
            if nn == 0:
                alpha_mat     = sp.csr_matrix(self.alpha_v(nn),
                                              shape=(1, N))
            else:
                alpha_v       = sp.csr_matrix(self.alpha_v(nn),
                                              shape=(1, N))
                alpha_mat     = sp.vstack([alpha_mat, alpha_v])
        self.alpha_mat = alpha_mat


    def Euler(self, t_v, flag=False):
        assert len(t_v) >= 2, "This time grid cannot be used for time stepping."

        h     = t_v[1] - t_v[0]

        x_v   = np.array([self.x[0]])
        y_v   = np.array([self.x[1]])
        z_v   = np.array([self.x[2]])

        u10, u20, u30 = self.vel.get_velocity(self.x[0], self.x[1], self.x[2], t_v[0])
        w1_v  = np.array([self.w[0]])
        w2_v  = np.array([self.w[1]])
        w3_v  = np.array([self.w[2]])

        xi    = self.p.R * np.sqrt(3 / self.p.S) * np.sqrt(h / np.pi)

        for nn in range(0, len(t_v)-1):

            # TODO : why make it a csr matrix if you transform it back to a dense array ?
            Sum_w1        = np.dot(self.alpha_mat.toarray()[nn, :nn+1], w1_v)
            Sum_w2        = np.dot(self.alpha_mat.toarray()[nn, :nn+1], w2_v)
            Sum_w3        = np.dot(self.alpha_mat.toarray()[nn, :nn+1], w3_v)

            if nn == 0:
                x_np1     = x_v[nn] + h * (w1_v[0] + u10)
                y_np1     = y_v[nn] + h * (w2_v[0] + u20)
                z_np1     = z_v[nn] + h * (w3_v[0] + u30)
            else:
                u1_n, u2_n, u3_n  = self.vel.get_velocity(x_v[nn], y_v[nn], z_v[nn], t_v[nn])

                x_np1     = x_v[nn] + h * (w1_v[0] + u1_n)
                y_np1     = y_v[nn] + h * (w2_v[0] + u2_n)
                z_np1     = z_v[nn] + h * (w3_v[0] + u3_n)

            G1, G2, G3    = self.calculate_G(w1_v[0], w2_v[0], w3_v[0],
                                        x_v[nn], y_v[nn], z_v[nn],
                                        t_v[nn])

            Gw1_n         = G1 - (self.p.R / self.p.S) * w1_v[0] - (1 - self.p.R) * 0.0
            Gw2_n         = G2 - (self.p.R / self.p.S) * w2_v[0] - (1 - self.p.R) * 0.0
            Gw3_n         = G3 - (self.p.R / self.p.S) * w3_v[0] - (1 - self.p.R) * self.p.g


            w1_np1        = ( w1_v[0] + h * Gw1_n - xi * Sum_w1 ) / \
                            (1.0 + xi * self.alpha_jn(0, nn+1))
            w2_np1        = ( w2_v[0] + h * Gw2_n - xi * Sum_w2 ) / \
                            (1.0 + xi * self.alpha_jn(0, nn+1))
            w3_np1        = ( w3_v[0] + h * Gw3_n - xi * Sum_w3 ) / \
                            (1.0 + xi * self.alpha_jn(0, nn+1))


            x_v        = np.append(x_v, x_np1)
            y_v        = np.append(y_v, y_np1)
            z_v        = np.append(z_v, z_np1)
            w1_v       = np.append(w1_np1, w1_v)
            w2_v       = np.append(w2_np1, w2_v)
            w3_v       = np.append(w3_np1, w3_v)

        pos_vec_x      = x_v
        pos_vec_y      = y_v
        pos_vec_z      = z_v
        w_vec          = np.transpose(np.array([np.flip(w1_v), np.flip(w2_v), np.flip(w3_v)]))

        if flag == True:
            self.pos_vec_x = np.copy(pos_vec_x)
            self.pos_vec_y = np.copy(pos_vec_y)
            self.pos_vec_z = np.copy(pos_vec_z)
            self.w_vec     = np.copy(w_vec)

        return pos_vec_x, pos_vec_y, pos_vec_z, w_vec


    def beta_jn(self, j, n):

        if n == 0:
            return 0.0

        elif n == 1:
            return self.alpha_jn(j, n)

        elif n == 2:
            if j == 0:
                return 12.0 * np.sqrt(2.0) / 15.0
            elif j == 1:
                return 16.0 * np.sqrt(2.0) / 15.0
            elif j == 2:
                return 2.0 * np.sqrt(2.0) / 15.0

        elif n == 3:
            if j == 0:
                return 4.0 * np.sqrt(2.0) / 5.0
            elif j == 1:
                return (14.0 * np.sqrt(3.0) - 12.0 * np.sqrt(2.0)) / 5.0
            elif j == 2:
                return (12.0 * np.sqrt(2.0) - 8.0 * np.sqrt(3.0)) / 5.0
            elif j == 3:
                return (np.sqrt(3.0) - np.sqrt(2.0)) * (4.0 / 5.0)

        else:
            if j == 0:
                return 4.0 * np.sqrt(2.0) / 5.0
            elif j == 1:
                return (14.0 * np.sqrt(3.0) - 12.0 * np.sqrt(2.0)) / 5.0
            elif j == 2:
                return (176.0/15.0) + ( 12.0 * np.sqrt(2.0) - 42.0 * np.sqrt(3.0)) / 5.0
            elif j == n-1:
                return (8.0/15.0) * (-2.0 * n**(5.0/2.0) + \
                              3.0 * (n - 1.0)**(5.0/2.0) - \
                                    (n - 2.0)**(5.0/2.0)) + \
                         (2.0/3.0) * (4.0 * n**(3.0/2.0) - \
                              3.0 * (n - 1.0)**(3.0/2.0) + \
                                    (n - 2.0)**(3.0/2.0))
            elif j == n:
                return (8.0/15.0) * (       n**(5.0/2.0) - \
                                    (n - 1.0)**(5.0/2.0)) + \
                        (2.0/3.0) * (-3.0 * n**(3.0/2.0) + \
                                    (n - 1.0)**(3.0/2.0)) + \
                                    2.0 * np.sqrt(n)
            else:
                return (8.0/15.0) * ((j + 2.0)**(5.0/2.0) - \
                               3.0 * (j + 1.0)**(5.0/2.0) + \
                                       3.0 * j**(5.0/2.0) - \
                                     (j - 1.0)**(5.0/2.0)) + \
                       (2.0/3.0) * (-(j + 2.0)**(3.0/2.0) + \
                               3.0 * (j + 1.0)**(3.0/2.0) - \
                                       3.0 * j**(3.0/2.0) + \
                                     (j - 1.0)**(3.0/2.0))



    def beta_v(self, N):

        BetaSubst_v = np.array([])
        for nn in range(0, N+1):
            BetaSubst_v = np.append(BetaSubst_v,
                              self.beta_jn(nn+1, N+1) -\
                                  self.beta_jn(nn, N))

        return BetaSubst_v



    def calc_beta_mat(self, N):
        for nn in range(0, N-1):
            if nn == 0:
                beta_mat     = sp.csr_matrix(self.beta_v(nn), shape=(1, N))
            else:
                beta_v       = sp.csr_matrix(self.beta_v(nn), shape=(1, N))
                beta_mat     = sp.vstack([beta_mat, beta_v])
        self.beta_mat = beta_mat



    def AdamBashf2(self, t_v, flag=False):
        assert len(t_v) >= 2, "Time grid cannot be used for time stepping."

        h          = t_v[1] - t_v[0]

        # Obtaining first time step with a 1st order method
        t_np1           = np.linspace(t_v[0], t_v[1], self.euler_nodes)
        pos_vec_x, pos_vec_y, pos_vec_z, w_vec = self.Euler(t_np1, flag=False)

        # Calculating the rest of the solution with a 2nd order method

        x_v   = np.array([self.x[0], pos_vec_x[-1]])
        y_v   = np.array([self.x[1], pos_vec_y[-1]])
        z_v   = np.array([self.x[2], pos_vec_z[-1]])

        u10, u20, u30  = self.vel.get_velocity(self.x[0], self.x[1], self.x[2], t_v[0])

        w1_v   = np.array([w_vec[-1,0], self.w[0]])
        w2_v   = np.array([w_vec[-1,1], self.w[1]])
        w3_v   = np.array([w_vec[-1,2], self.w[2]])

        xi    = (self.p.R) * np.sqrt(3 / self.p.S) * np.sqrt(h / np.pi)

        for nn in range(1, len(t_v)-1):
            Sum_w1     = np.dot(self.beta_mat.toarray()[nn, :nn+1], w1_v)
            Sum_w2     = np.dot(self.beta_mat.toarray()[nn, :nn+1], w2_v)
            Sum_w3     = np.dot(self.beta_mat.toarray()[nn, :nn+1], w3_v)

            u1_n, u2_n, u3_n       = self.vel.get_velocity(x_v[nn], y_v[nn], z_v[nn], t_v[nn])
            u1_nm1, u2_nm1, u3_nm1 = self.vel.get_velocity(x_v[nn-1], y_v[nn-1], z_v[nn-1], t_v[nn-1])

            x_np1     = x_v[nn] + (h/2.0) * ( 3.0 * (w1_v[0] + u1_n) - (w1_v[1] + u1_nm1))
            y_np1     = y_v[nn] + (h/2.0) * ( 3.0 * (w2_v[0] + u2_n) - (w2_v[1] + u2_nm1))
            z_np1     = z_v[nn] + (h/2.0) * ( 3.0 * (w3_v[0] + u3_n) - (w3_v[1] + u3_nm1))

            G1_n, G2_n, G3_n  = self.calculate_G(w1_v[0], w2_v[0], w3_v[0],
                                        x_v[nn], y_v[nn], z_v[nn],
                                        t_v[nn])
            G1_nm1, G2_nm1, G3_nm1 = self.calculate_G(w1_v[1], w2_v[1], w3_v[1],
                                        x_v[nn-1], y_v[nn-1], z_v[nn-1],
                                        t_v[nn-1])


            Gw1_n      = G1_n - (self.p.R / self.p.S) * w1_v[0]
            Gw2_n      = G2_n - (self.p.R / self.p.S) * w2_v[0]
            Gw3_n      = G3_n - (self.p.R / self.p.S) * w3_v[0] - (1 - self.p.R) * self.p.g

            Gw1_nm1    = G1_nm1 - (self.p.R / self.p.S) * w1_v[1]
            Gw2_nm1    = G2_nm1 - (self.p.R / self.p.S) * w2_v[1]
            Gw3_nm1    = G3_nm1 - (self.p.R / self.p.S) * w3_v[1] - (1 - self.p.R) * self.p.g

            w1_np1     = ( w1_v[0] + (h/2.0) * (3.0 * Gw1_n - Gw1_nm1) - xi * Sum_w1 ) / \
                            (1.0 + xi * self.beta_jn(0, nn+1))
            w2_np1     = ( w2_v[0] + (h/2.0) * (3.0 * Gw2_n - Gw2_nm1) - xi * Sum_w2 ) / \
                            (1.0 + xi * self.beta_jn(0, nn+1))
            w3_np1     = ( w3_v[0] + (h/2.0) * (3.0 * Gw3_n - Gw3_nm1) - xi * Sum_w3 ) / \
                            (1.0 + xi * self.beta_jn(0, nn+1))



            x_v        = np.append(x_v, x_np1)
            y_v        = np.append(y_v, y_np1)
            z_v        = np.append(z_v, z_np1)
            w1_v       = np.append(w1_np1, w1_v)
            w2_v       = np.append(w2_np1, w2_v)
            w3_v       = np.append(w3_np1, w3_v)

        pos_vec_x      = x_v
        pos_vec_y      = y_v
        pos_vec_z      = z_v
        w_vec          = np.transpose(np.array([np.flip(w1_v), np.flip(w2_v), np.flip(w3_v)]))

        if flag == True:
            self.pos_vec_x = np.copy(pos_vec_x)
            self.pos_vec_y = np.copy(pos_vec_y)
            self.pos_vec_z = np.copy(pos_vec_z)
            self.w_vec     = np.copy(w_vec)

        return pos_vec_x, pos_vec_y, pos_vec_z, w_vec

    def gamma_jn(self, j, n):

        if n == 0:
          gamma = 0.0

        elif n == 1:
            gamma = self.alpha_jn(j, n)

        elif n == 2:
            gamma = self.beta_jn(j, n)

        elif n == 3:
            if j == 0:
                gamma = (68.0/105.0) * np.sqrt(3.0)
            elif j == 1:
                gamma = (6.0/7.0) * np.sqrt(3.0)
            elif j == 2:
                gamma = (12.0/35.0) * np.sqrt(3.0)
            elif j == 3:
                gamma = (16.0/105.0) * np.sqrt(3.0)

        elif n == 4:
            if j == 0:
                gamma = (244.0/315.0) * np.sqrt(2.0)
            elif j == 1:
                gamma = (1888.0 - 976.0 * np.sqrt(2.0)) / 315.0
            elif j == 2:
                gamma = (488.0 * np.sqrt(2.0) - 656.0 ) / 105.0
            elif j == 3:
                gamma = (544.0/105.0) - (976.0/315.0) * np.sqrt(2.0)
            elif j == 4:
                gamma = (244.0 * np.sqrt(2.0) - 292.0 ) / 315.0

        elif n == 5:
            if j == 0:
                gamma = (244.0/315.0) * np.sqrt(2.0)
            elif j == 1:
                gamma = (362.0/105.0) * np.sqrt(3.0) - (976.0/315.0) * np.sqrt(2.0)
            elif j == 2:
                gamma = (500.0/63.0) * np.sqrt(5.0) - \
                            (1448.0/105.0) * np.sqrt(3.0) + \
                                (488.0/105.0) * np.sqrt(2.0)
            elif j == 3:
                gamma = (-290.0/21.0) * np.sqrt(5.0) + \
                            (724.0/35.0) * np.sqrt(3.0) - \
                                (976.0/315.0) * np.sqrt(2.0)
            elif j == 4:
                gamma = (220.0/21.0) * np.sqrt(5.0) - \
                            (1448.0/105.0) * np.sqrt(3.0) + \
                                (244.0/315.0) * np.sqrt(2.0)
            elif j == 5:
                gamma = (362.0/105.0) * np.sqrt(3.0) - \
                            (164.0/63.0) * np.sqrt(5.0)

        elif n == 6:
            if j == 0:
                gamma = (244.0/315.0) * np.sqrt(2.0)
            elif j == 1:
                gamma = (362.0/105.0) * np.sqrt(3.0) - \
                            (976.0/315.0) * np.sqrt(2.0)
            elif j == 2:
                gamma = (5584.0/315.0) - \
                            (1448.0/105.0) * np.sqrt(3.0) + \
                                (488.0/105.0) * np.sqrt(2.0)
            elif j == 3:
                gamma = (344.0/21.0) * np.sqrt(6.0) - \
                            (22336.0/315.0) + (724.0/35.0) * np.sqrt(3.0) - \
                                (976.0/315.0) * np.sqrt(2.0)
            elif j == 4:
                gamma = (-1188.0/35.0) * np.sqrt(6.0) + \
                            (11168.0/105.0) - (1448.0/105.0) * np.sqrt(3.0) + \
                                (244.0/315.0) * np.sqrt(2.0)
            elif j == 5:
                gamma = (936.0/35.0) * np.sqrt(6.0) - \
                            (22336.0/315.0) + (362.0/105.0) * np.sqrt(3.0)
            elif j == 6:
                gamma = (5584.0/315.0) - (754.0/105.0) * np.sqrt(6.0)

        else:
            if j == 0:
                gamma = 244.0 * np.sqrt(2.0) / 315.0

            elif j == 1:
                gamma = (362.0/105.0) * np.sqrt(3.0) - \
                            (976.0/315.0) * np.sqrt(2.0)

            elif j == 2:
                gamma = (5584.0/315.0) - (1448.0/105.0) * np.sqrt(3.0) + \
                            (488.0/105.0) * np.sqrt(2.0)

            elif j == 3:
                gamma = (1130.0/63.0) * np.sqrt(5.0) - \
                            (22336.0/315.0) + (724.0/35.0) * np.sqrt(3.0) - \
                                (976.0/315.0) * np.sqrt(2.0)

            elif j == n-3:
                gamma = (16.0/105.0) * (n**(7.0/2.0) - \
                            4.0 * (n - 2.0)**(7.0/2.0) + \
                            6.0 * (n - 3.0)**(7.0/2.0) - \
                            4.0 * (n - 4.0)**(7.0/2.0) + \
                                    (n - 5.0)**(7.0/2.0)) - \
                                (8.0/15.0) * n**(5.0/2.0) + \
                                (4.0/9.0) * n**(3.0/2.0) + \
                        (8.0/9.0) * (n - 2.0)**(3.0/2.0) - \
                        (4.0/3.0) * (n - 3.0)**(3.0/2.0) + \
                        (8.0/9.0) * (n - 4.0)**(3.0/2.0) - \
                        (2.0/9.0) * (n - 5.0)**(3.0/2.0)
            elif j == n-2:
                gamma = (16.0/105.0) * ((n - 4.0)**(7.0/2.0) - \
                                    4.0 * (n - 3.0)**(7.0/2.0) + \
                                    6.0 * (n - 2.0)**(7.0/2.0) - \
                                        3.0 * n ** (7.0/2.0)) + \
                                    (32.0/15.0) * n**(5.0/2.0) - \
                                            2.0 * n**(3.0/2.0) - \
                            (4.0/3.0) * (n - 2.0)**(3.0/2.0) + \
                            (8.0/9.0) * (n - 3.0)**(3.0/2.0) - \
                            (2.0/9.0) * (n - 4.0)**(3.0/2.0)
            elif j == n-1:
                gamma = (16.0/105.0) * ( 3.0 * n**(7.0/2.0) - \
                                4.0 * (n - 2.0)**(7.0/2.0) + \
                                        (n - 3.0)**(7.0/2.0)) - \
                                    (8.0/3.0) * n**(5.0/2.0) + \
                                        4.0 * n **(3.0/2.0) + \
                            (8.0/9.0) * (n - 2.0)**(3.0/2.0) - \
                            (2.0/9.0) * (n - 3.0)**(3.0/2.0)
            elif j == n:
                gamma = (16.0/105.0) * ((n - 2.0)**(7.0/2.0) - \
                                                n**(7.0/2.0)) + \
                                    (16.0/15.0) * n**(5.0/2.0) - \
                                    (22.0/9.0) * n**(3.0/2.0) - \
                            (2.0/9.0) * (n - 2.0)**(3.0/2.0) + \
                                    2.0 * np.sqrt(n)
            else:
                gamma = (16.0/105.0) * ((j + 2.0)**(7.0/2.0) + \
                                        (j - 2.0)**(7.0/2.0) - \
                                    4.0 * (j + 1.0)**(7.0/2.0) - \
                                    4.0 * (j - 1.0)**(7.0/2.0) + \
                                            6.0 * j**(7.0/2.0)) + \
                    (2.0/9.0) * (4.0 * (j + 1.0)**(3.0/2.0) + \
                                4.0 * (j - 1.0)**(3.0/2.0) - \
                                        (j + 2.0)**(3.0/2.0) - \
                                        (j - 2.0)**(3.0/2.0) - \
                                        6.0 * j**(3.0/2.0))
        return gamma



    def gamma_v(self, N):

        GammaSubst_v = np.array([])
        for nn in range(0, N+1):
            GammaSubst_v = np.append(GammaSubst_v, self.gamma_jn(nn+1, N+1) -\
                                                    self.gamma_jn(nn, N))

        return GammaSubst_v



    def calc_gamma_mat(self, N):
        for nn in range(0, N-1):
            if nn == 0:
                gamma_mat    = sp.csr_matrix(self.gamma_v(nn), shape=(1, N))
            else:
                gamma_v      = sp.csr_matrix(self.gamma_v(nn), shape=(1, N))
                gamma_mat    = sp.vstack([gamma_mat, gamma_v])
        self.gamma_mat = gamma_mat



    def AdamBashf3(self, t_v, flag=False):
        assert len(t_v) >= 3, "Time grid cannot be used for time stepping."

        h               = t_v[1] - t_v[0]

        # Obtaining first and second time steps with a 1st order method
        assert self.euler_nodes % 2 == 1, "Please provide an odd number of nodes for the Euler computation of the first steps."
        t_np1           = np.linspace(t_v[0], t_v[2], self.euler_nodes)
        pos_vec_x, pos_vec_y, pos_vec_z, w_vec = self.AdamBashf2(t_np1, flag=False)

        # Calculating the rest of the solution with a 3rd order method
        x_v      = np.array([self.x[0], pos_vec_x[int((self.euler_nodes-1)/2)], pos_vec_x[-1]])
        y_v      = np.array([self.x[1], pos_vec_y[int((self.euler_nodes-1)/2)], pos_vec_y[-1]])
        z_v      = np.array([self.x[2], pos_vec_z[int((self.euler_nodes-1)/2)], pos_vec_z[-1]])


        u10, u20, u30  = self.vel.get_velocity(self.x[0], self.x[1], self.x[2], t_v[0])

        w1_v = np.array([w_vec[-1,0], w_vec[int((self.euler_nodes-1)/2),0], self.w[0]])
        w2_v = np.array([w_vec[-1,1], w_vec[int((self.euler_nodes-1)/2),1], self.w[1]])
        w3_v = np.array([w_vec[-1,2], w_vec[int((self.euler_nodes-1)/2),2], self.w[2]])

        xi    = (self.p.R) * np.sqrt(3 / self.p.S) * np.sqrt(h / np.pi)

        for nn in range(2, len(t_v)-1):
            Sum_w1        = np.dot(self.gamma_mat.toarray()[nn, :nn+1], w1_v)
            Sum_w2        = np.dot(self.gamma_mat.toarray()[nn, :nn+1], w2_v)
            Sum_w3        = np.dot(self.gamma_mat.toarray()[nn, :nn+1], w3_v)


            u1_n, u2_n, u3_n = self.vel.get_velocity(x_v[nn], y_v[nn], z_v[nn], t_v[nn])
            u1_nm1, u2_nm1, u3_nm1 = self.vel.get_velocity(x_v[nn-1], y_v[nn-1], z_v[nn-1], t_v[nn-1])
            u1_nm2, u2_nm2, u3_nm2 = self.vel.get_velocity(x_v[nn-2], y_v[nn-2], z_v[nn-2], t_v[nn-2])

            x_np1        = x_v[nn] + (h/12.0) * ( 23.0 * (w1_v[0] + u1_n) -\
                                                    16.0 * (w1_v[1] + u1_nm1) +\
                                                    5.0 * (w1_v[2] + u1_nm2))
            y_np1        = y_v[nn] + (h/12.0) * ( 23.0 * (w2_v[0] + u2_n) -\
                                                    16.0 * (w2_v[1] + u2_nm1) +\
                                                    5.0 * (w2_v[2] + u2_nm2))
            z_np1        = z_v[nn] + (h/12.0) * ( 23.0 * (w3_v[0] + u3_n) -\
                                                    16.0 * (w3_v[1] + u3_nm1) +\
                                                    5.0 * (w3_v[2] + u3_nm2))


            G1_n, G2_n, G3_n     = self.calculate_G(w1_v[0],  w2_v[0], w3_v[0],
                                            x_v[nn], y_v[nn], z_v[nn],
                                            t_v[nn])
            G1_nm1, G2_nm1, G3_nm1 = self.calculate_G(w1_v[1],  w2_v[1], w3_v[1],
                                            x_v[nn-1], y_v[nn-1], z_v[nn-1],
                                            t_v[nn-1])
            G1_nm2, G2_nm2, G3_nm2 = self.calculate_G(w1_v[2],  w2_v[2], w3_v[2],
                                            x_v[nn-2], y_v[nn-2], z_v[nn-2],
                                            t_v[nn-2])


            Gw1_n      = G1_n   - (self.p.R / self.p.S) * w1_v[0]
            Gw2_n      = G2_n   - (self.p.R / self.p.S) * w2_v[0]
            Gw3_n      = G3_n   - (self.p.R / self.p.S) * w3_v[0] - (1 - self.p.R) * self.p.g

            Gw1_nm1    = G1_nm1 - (self.p.R / self.p.S) * w1_v[1]
            Gw2_nm1    = G2_nm1 - (self.p.R / self.p.S) * w2_v[1]
            Gw3_nm1    = G3_nm1 - (self.p.R / self.p.S) * w3_v[1] - (1 - self.p.R) * self.p.g

            Gw1_nm2    = G1_nm2 - (self.p.R / self.p.S) * w1_v[2]
            Gw2_nm2    = G2_nm2 - (self.p.R / self.p.S) * w2_v[2]
            Gw3_nm2    = G3_nm2 - (self.p.R / self.p.S) * w3_v[2] - (1 - self.p.R) * self.p.g



            w1_np1        = ( w1_v[0] + (h/12.0) * (23.0 * Gw1_n - \
                                16.0 * Gw1_nm1 + 5.0 * Gw1_nm2) - \
                                    xi * Sum_w1 ) / \
                            (1.0 + xi * self.gamma_jn(0, nn+1))
            w2_np1        = ( w2_v[0] + (h/12.0) * (23.0 * Gw2_n - \
                                16.0 * Gw2_nm1 + 5.0 * Gw2_nm2) - \
                                    xi * Sum_w2 ) / \
                            (1.0 + xi * self.gamma_jn(0, nn+1))
            w3_np1        = ( w3_v[0] + (h/12.0) * (23.0 * Gw3_n - \
                                16.0 * Gw3_nm1 + 5.0 * Gw3_nm2) - \
                                    xi * Sum_w3 ) / \
                            (1.0 + xi * self.gamma_jn(0, nn+1))


            x_v          = np.append(x_v, x_np1)
            y_v          = np.append(y_v, y_np1)
            z_v          = np.append(z_v, z_np1)
            w1_v         = np.append(w1_np1, w1_v)
            w2_v         = np.append(w2_np1, w2_v)
            w3_v         = np.append(w3_np1, w3_v)

        pos_vec_x      = x_v
        pos_vec_y      = y_v
        pos_vec_z      = z_v
        w_vec          = np.transpose(np.array([np.flip(w1_v), np.flip(w2_v), np.flip(w3_v)]))

        if flag == True:
            self.pos_vec_x = np.copy(pos_vec_x)
            self.pos_vec_y = np.copy(pos_vec_y)
            self.pos_vec_z = np.copy(pos_vec_z)
            self.w_vec     = np.copy(w_vec)

        return pos_vec_x, pos_vec_y, pos_vec_z, w_vec
