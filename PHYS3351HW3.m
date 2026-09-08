% Question 3(c) - Plot probability density |Phi_n(p,t)|^2 for n = 1, 2, 5, 10
clear all; close all; clc;
n = [1, 2, 5, 10];

figure;
for i = 1:4
    n_val = n(i);
    
    % Define the probability density function for current n
    phi_n = @(p) 2 * (n_val / pi)^2 * (1 - (-1)^n_val * cos(pi * p)) ./ (n_val^2 - p.^2).^2;
    
    % Find maximum by evaluating on a grid
    p_grid = linspace(-12, 12, 100000000);
    mom_grid = phi_n(p_grid);
    [max_mom, max_idx] = max(mom_grid);
    fprintf('n=%d: max |Phi_n(p,t)|^2 = %.6f at p = %.6f\n', n_val, max_mom, p_grid(max_idx));
    
    subplot(2, 2, i);
    fplot(phi_n, [-12, 12], 'b-', 'LineWidth', 1);
    title(sprintf('n = %d', n_val));
    xlabel('Momentum p');
    ylabel('|\Phi_n(p, t)|^2');
    grid on;
end