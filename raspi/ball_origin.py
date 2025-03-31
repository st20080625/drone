import numpy as np
def get_origin(xi, yi, zi):
    sigma_xi2 = np.sum(xi*xi)
    sigma_xiyi = np.sum(xi*yi)
    sigma_yi2 = np.sum(yi*yi)
    sigma_xizi = np.sum(xi*zi)
    sigma_yizi = np.sum(yi*zi)
    sigma_zi2 = np.sum(zi*zi)
    sigma_xi = np.sum(xi)
    sigma_yi = np.sum(yi)
    sigma_zi = np.sum(zi)
    sigma_1 = len(xi)
    sigma_xi3 = np.sum(xi*xi*xi)
    sigma_xiyi2 = np.sum(xi*yi*yi)
    sigma_xizi2 = np.sum(xi*zi*zi)
    sigma_yixi2 = np.sum(yi*xi*xi)
    sigma_yi3 = np.sum(yi*yi*yi)
    sigma_yizi2 = np.sum(yi*zi*zi)
    sigma_zixi2 = np.sum(zi*xi*xi)
    sigma_ziyi2 = np.sum(zi*yi*yi)
    sigma_zi3 = np.sum(zi*zi*zi)
    front = np.array(
        [[sigma_xi2, sigma_xiyi, sigma_xizi, sigma_xi],
        [sigma_xiyi, sigma_yi2, sigma_yizi, sigma_yi],
        [sigma_xizi, sigma_yizi, sigma_zi2, sigma_zi],
        [sigma_xi, sigma_yi, sigma_zi, sigma_1]])
    back = np.array(
        [(sigma_xi3+sigma_xiyi2+sigma_xizi2)*-1,
        (sigma_yixi2+sigma_yi3+sigma_yizi2)*-1,
        (sigma_zixi2+sigma_ziyi2+sigma_zi3)*-1,
        (sigma_xi2+sigma_yi2+sigma_zi2)*-1])
    A, B, C, D = np.linalg.solve(front, back.T)
    x0 = -A/2
    y0 = -B/2
    z0 = -C/2
    r = np.sqrt(-(D-x0**2-y0**2-z0**2))
    return x0, y0, z0, r