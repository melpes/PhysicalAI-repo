function passed = verify_matlab_robot(neutralPath, csvPath)
%VERIFY_MATLAB_ROBOT Check MATLAB forward kinematics of the neutral robot.
%   verify_matlab_robot('scenes/irb4600_40_255.neutral.xml', 'tests/irb4600_test_poses.csv')
%   Compares the wrist centre and J6 axis with the shared test poses, and the
%   two extreme poses with ABB's published working range values.

    tolerance = 1e-9;
    robot = read_neutral_robot(neutralPath);
    poses = readtable(csvPath, 'TextType', 'char');
    results = false(1, 0);
    results = report(results, 'XML 불러오기', true, sprintf('MATLAB %s, %s', version('-release'), robot.model));
    results = report(results, '관절 수', numel(robot.joints) == 6, sprintf('%d개', numel(robot.joints)));

    jointIds = {robot.joints.id};
    for r = 1:height(poses)
        poseId = poses.pose_id{r};
        q = cellfun(@(id) poses.(id)(r), jointIds);
        linkPoses = robot_link_poses(robot, q);
        wristPose = linkPoses('WristCenter');
        wrist = wristPose.p;
        expected = [poses.wc_x(r) poses.wc_y(r) poses.wc_z(r)];
        err = max(abs(wrist - expected));
        results = report(results, [poseId ' 손목중심 위치'], err < tolerance, ...
            sprintf('MATLAB %s / 기준 %s (오차 %.1e m)', mat2str(wrist, 6), mat2str(expected, 6), err));

        j6 = robot.joints(end);
        j6Pose = linkPoses(j6.child);
        axisWorld = (j6Pose.R * j6.axis(:)).';
        expectedAxis = [poses.j6_axis_x(r) poses.j6_axis_y(r) poses.j6_axis_z(r)];
        axisErr = max(abs(axisWorld - expectedAxis));
        results = report(results, [poseId ' J6 축 방향'], axisErr < tolerance, sprintf('오차 %.1e', axisErr));

        switch poseId
            case 'abb_max_reach'
                value = hypot(wrist(1), wrist(2)) * 1000;
                results = report(results, 'ABB 공개값 앞쪽 수평 도달거리', abs(value - 2552) < 1, ...
                    sprintf('MATLAB %.1f mm / ABB 2552 mm', value));
            case 'abb_max_back_reach'
                value = hypot(wrist(1), wrist(2)) * 1000;
                results = report(results, 'ABB 공개값 뒤쪽 수평 도달거리', abs(value - 2202) < 1, ...
                    sprintf('MATLAB %.1f mm / ABB 2202 mm', value));
            case 'abb_max_depth'
                value = -wrist(3) * 1000;
                results = report(results, 'ABB 공개값 베이스 아래 최저 깊이', abs(value - 1735) < 1, ...
                    sprintf('MATLAB %.1f mm / ABB 1735 mm', value));
            case 'abb_max_height'
                value = wrist(3) * 1000;
                results = report(results, 'ABB 공개값 최고 높이', abs(value - 2872) < 1, ...
                    sprintf('MATLAB %.1f mm / ABB 2872 mm', value));
        end
    end
    fprintf('\n%d/%d 통과\n', sum(results), numel(results));
    passed = all(results);
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
