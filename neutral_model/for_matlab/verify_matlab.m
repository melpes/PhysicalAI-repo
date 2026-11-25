function passed = verify_matlab(neutralPath, mPath)
%VERIFY_MATLAB Check that a generated MATLAB script draws the neutral boxes exactly.
%   verify_matlab('scenes/box.neutral.xml', 'for_matlab/outputs/box_matlab.m')
%   The neutral XML is the reference. The script is run, and every patch it
%   draws is compared with values computed independently from the XML.

    tolerance = 1e-9;
    corners = [-1 -1 -1; 1 -1 -1; 1 1 -1; -1 1 -1; ...
               -1 -1 1; 1 -1 1; 1 1 1; -1 1 1];
    objects = read_neutral_scene(neutralPath);
    results = false(1, 0);
    results = report(results, 'XML 불러오기', true, sprintf('MATLAB %s, 객체 %d개', version('-release'), numel(objects)));

    run(mPath);
    fig = gcf;
    for obj = objects
        h = findobj(fig, 'Type', 'patch', 'Tag', obj.id);
        results = report(results, [obj.id ' 존재'], isscalar(h), sprintf('Tag가 %s인 patch %d개', obj.id, numel(h)));
        if ~isscalar(h)
            continue;
        end
        V = h.Vertices;
        F = h.Faces;
        results = report(results, [obj.id ' 형상'], isequal(size(V), [8 3]) && isequal(size(F), [6 4]), ...
            sprintf('꼭짓점 %d개, 면 %d개', size(V, 1), size(F, 1)));

        edges = [norm(V(2, :) - V(1, :)), norm(V(4, :) - V(1, :)), norm(V(5, :) - V(1, :))];
        results = report(results, [obj.id ' 크기(전체 길이)'], max(abs(edges - obj.size)) < tolerance, ...
            sprintf('MATLAB %s / 중립 %s', mat2str(edges, 6), mat2str(obj.size, 6)));

        center = mean(V, 1);
        results = report(results, [obj.id ' 위치'], max(abs(center - obj.position)) < tolerance, ...
            sprintf('MATLAB %s / 중립 %s', mat2str(center, 6), mat2str(obj.position, 6)));

        R = axisAngleRotation(obj.orientation);
        xAxis = (V(2, :) - V(1, :)) / edges(1);
        results = report(results, [obj.id ' 회전'], max(abs(xAxis - R(:, 1).')) < tolerance, ...
            sprintf('박스 x축 방향 MATLAB %s / 중립 %s', mat2str(xAxis, 6), mat2str(R(:, 1).', 6)));

        results = report(results, [obj.id ' 색'], ...
            max(abs([h.FaceColor h.FaceAlpha] - obj.color)) < 1e-12, ...
            sprintf('MATLAB %s / 중립 %s', mat2str([h.FaceColor h.FaceAlpha], 6), mat2str(obj.color, 6)));

        expected = (corners .* (obj.size/2)) * R.' + obj.position;
        err = max(abs(V - expected), [], 'all');
        results = report(results, [obj.id ' 꼭짓점 8개'], err < tolerance, sprintf('최대 오차 %.2e m', err));
    end
    fprintf('\n%d/%d 통과\n', sum(results), numel(results));
    passed = all(results);
end

function R = axisAngleRotation(q)
% Rodrigues formula: an independent route from the quaternion to the
% rotation matrix, so the check does not reuse the formula in drawBox.
    q = q / norm(q);
    s = sqrt(max(0, 1 - q(1)^2));
    if s < 1e-12
        R = eye(3);
        return;
    end
    theta = 2 * acos(q(1));
    a = q(2:4) / s;
    K = [0 -a(3) a(2); a(3) 0 -a(1); -a(2) a(1) 0];
    R = eye(3) + sin(theta) * K + (1 - cos(theta)) * (K * K);
end

function results = report(results, label, passed, detail)
    results(end+1) = passed;
    if passed
        status = 'PASS';
    else
        status = 'FAIL';
    end
    fprintf('[%s] %s: %s\n', status, label, detail);
end
