# State log: gnc-plane-3day-pilot

# Run started 2026-04-27 00:18 (driven from parent session — see req.md "Pipeline behavior overrides")

2026-04-27 00:18:00  preflight   start          slug=gnc-plane-3day-pilot
2026-04-27 00:18:28  preflight   ok             agents-present=7 waf-present=yes sim_vehicle-present=yes branch=GNC-0.1 sha=98325ac0cc
2026-04-27 00:18:28  req-locked  ok             path=course/orchestration/gnc-plane-3day-pilot/req.md
2026-04-27 00:18:42  stage-1     iter=1  planner-spawn
2026-04-27 00:33:13  stage-1     iter=1  planner-done plan=course/plans/plan-gnc-plane-3day-pilot-iter1.md
2026-04-27 00:33:17  stage-1     iter=1  writer-spawn
2026-04-27 00:45:25  stage-1     iter=1  writer-done course=course/custom_gnc_course_plane_3day_pilot.md
2026-04-27 00:45:25  stage-1     iter=1  reviewer-spawn
2026-04-27 00:56:37  stage-1     iter=1  reviewer-done verdict=PASS-WITH-FIXES review=course/reviews/review-plan-gnc-plane-3day-pilot-iter1.md
2026-04-27 00:56:38  stage-1     iter=1  decision=loop-iter2 reason=blocker-F1-EKF-code-fabricated cap-remaining=2
2026-04-27 00:56:41  stage-1     iter=2  planner-spawn
2026-04-27 01:12:27  stage-1     iter=2  planner-done plan=course/plans/plan-gnc-plane-3day-pilot-iter2.md
2026-04-27 01:12:27  stage-1     iter=2  writer-spawn
2026-04-27 01:19:23  stage-1     iter=2  writer-done course=course/custom_gnc_course_plane_3day_pilot.md
2026-04-27 01:19:23  stage-1     iter=2  reviewer-spawn
2026-04-27 01:26:49  stage-1     iter=2  reviewer-done verdict=PASS review=course/reviews/review-plan-gnc-plane-3day-pilot-iter2.md
2026-04-27 01:26:49  stage-1                exit  verdict=PASS final-plan=plan-gnc-plane-3day-pilot-iter2.md
2026-04-27 01:26:58  stage-2                start lab-count=5 mode=batch-then-individual-tests
2026-04-27 01:52:17  stage-2     lab=all       lab-builder-done labs=5
2026-04-27 01:52:46  stage-2     lab=l1        lab-tester-spawn
2026-04-27 02:36:31  stage-2     lab=l1        lab-tester-done verdict=FAIL report=course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/runs/2026-04-27-0001/report.md
2026-04-27 02:36:31  stage-2     lab=l1        decision=lab-builder-iter2 reason=harness-defects content-correct iter-remaining=1
2026-04-27 02:36:31  stage-2     lab=l1        lab-builder-spawn iter=2
2026-04-27 02:40:25  stage-2     lab=l1        lab-builder-done iter=2 files=test.sh,test.py,steps.md,student-guide.md,instructor-guide.md
2026-04-27 02:40:25  stage-2     lab=l1        lab-tester-spawn iter=2
2026-04-27 02:43:47  stage-2     lab=l1        lab-tester-done iter=2 verdict=PASS report=course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/runs/2026-04-27-0002/report.md
2026-04-27 02:43:47  stage-2     lab=l2        lab-tester-spawn
2026-04-27 02:49:08  stage-2     lab=l2        lab-tester-done verdict=PASS report=course/labs/gnc-plane-3day-pilot-l2-apparam-add/runs/2026-04-27-0200/report.md note=patch-format-defect-non-blocking
2026-04-27 02:49:08  stage-2     lab=l3        lab-tester-spawn
2026-04-27 03:12:06  stage-2     lab=l3        lab-tester-done verdict=PASS report=course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch/runs/2026-04-27-0001/report.md note=3-non-blocking-harness-issues
2026-04-27 03:12:06  stage-2     lab=l4        lab-tester-spawn
2026-04-27 03:52:39  stage-2     lab=l4        lab-tester-done iter=1 verdict=FAIL report=course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/runs/2026-04-27-0000/report.md note=harness-defects-content-sound
2026-04-27 03:52:39  stage-2     lab=l4        decision=lab-builder-iter2 reason=harness-defects iter-remaining=1
2026-04-27 03:52:39  stage-2     lab=l4        lab-builder-spawn iter=2
2026-04-27 03:59:43  stage-2     lab=l4        lab-builder-done iter=2 files=test.py,steps.md,student-guide.md,README.md,instructor-guide.md
2026-04-27 03:59:43  stage-2     lab=l4        lab-tester-spawn iter=2
2026-04-27 04:10:59  stage-2     lab=l4        lab-tester-done iter=2 verdict=FAIL report=course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/runs/2026-04-27-0400/report.md note=defect3-content-issue-altitude-step-too-short
2026-04-27 04:10:59  stage-2     lab=l4        cap-hit       iters=2 verdict=FAIL surfacing-to-user
2026-04-27 06:04:03  stage-2     lab=l4        decision=raise-cap-to-3 user-approved
2026-04-27 06:04:03  stage-2     lab=l4        lab-builder-spawn iter=3
2026-04-27 06:07:38  stage-2     lab=l4        lab-builder-done iter=3 threshold=8m wall=8s files=test.py,expected.md,steps.md,student-guide.md,instructor-guide.md
2026-04-27 06:07:38  stage-2     lab=l4        lab-tester-spawn iter=3
2026-04-27 06:23:44  stage-2     lab=l4        cap-hit-2     iters=3 verdict=FAIL surfacing-to-user
2026-04-27 06:23:44  stage-2     lab=l4        decision=raise-total-cap-to-22 user-approved
2026-04-27 06:23:44  stage-2     lab=l4        lab-builder-spawn iter=4
2026-04-27 06:25:33  stage-2     lab=l4        lab-builder-done iter=4 wait-for-landing-added files=test.py,README.md
2026-04-27 06:25:33  stage-2     lab=l4        lab-tester-spawn iter=4
2026-04-27 06:53:45  stage-2     lab=l4        lab-tester-done iter=4 verdict=FAIL report=course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/runs/2026-04-27-0001/report.md note=ALT_HOLD_RTL-default-no-autoland
2026-04-27 06:53:45  stage-2     lab=l4        cap-hit-3     iters=4 surfacing-to-user
2026-04-27 06:53:45  stage-2     lab=l4        decision=freeze-known-issue user-approved final-verdict=FAIL phase-a-pass
2026-04-27 06:53:45  stage-2     lab=l5        lab-tester-spawn
2026-04-27 07:01:38  stage-2     lab=l5        lab-tester-done iter=1 verdict=FAIL note=5-build-infra-defects
2026-04-27 07:01:38  stage-2     lab=l5        cap-hit       iters=1 verdict=FAIL surfacing-to-user
2026-04-27 07:01:38  stage-2     lab=l5        decision=raise-cap-to-24 user-approved
2026-04-27 07:01:38  stage-2     lab=l5        lab-builder-spawn iter=2
2026-04-27 07:04:23  stage-2     lab=l5        lab-builder-done iter=2 fixes=A-B-C-D-E files=test.sh,3xCMakeLists.txt,2xmock_storage.cpp,README.md
2026-04-27 07:04:23  stage-2     lab=l5        lab-tester-spawn iter=2
2026-04-27 07:08:27  stage-2     lab=l5        lab-tester-done iter=2 verdict=FAIL note=defect-D-incomplete-gtest_main-missing-time.h
2026-04-27 07:08:27  stage-2     lab=l5        cap-hit-2     iters=2 verdict=FAIL surfacing-to-user
2026-04-27 07:08:27  stage-2     lab=l5        decision=raise-cap-to-25 user-approved
2026-04-27 07:08:27  stage-2     lab=l5        lab-builder-spawn iter=3
2026-04-27 07:10:09  policy      cap-update    user-directive max-lab-iters=10 total-cap=uncapped reason=try-harder-finish-everything
2026-04-27 07:10:15  stage-2     lab=l5        lab-builder-spawn iter=3
2026-04-27 07:10:15  stage-2     lab=l4        lab-builder-spawn iter=5
2026-04-27 07:13:21  stage-2     lab=l5        lab-builder-done iter=3 fixes=gtest_main+test-exe-time-include local-build-verified
2026-04-27 07:13:21  stage-2     lab=l5        lab-tester-spawn iter=3
2026-04-27 07:16:49  stage-2     lab=l5        lab-tester-done iter=3 verdict=PASS report=course/labs/gnc-plane-3day-pilot-l5-capstone/runs/2026-04-27-0714/report.md
2026-04-27 07:24:28  stage-2     lab=l4        lab-builder-done iter=5 approach=force-disarm-not-RTL-autoland matches-canonical-arduplane.py
2026-04-27 07:24:28  stage-2     lab=l4        lab-tester-spawn iter=5
2026-04-27 07:28:39  stage-2     lab=l4        lab-tester-done iter=5 verdict=PASS report=course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/runs/2026-04-27-0001-iter5/report.md wall=19s
2026-04-27 07:28:39  stage-2                exit  all-labs-PASS L1=PASS L2=PASS L3=PASS L4=PASS L5=PASS
2026-04-27 07:28:39  stage-3                start material-builder-spawn
2026-04-27 08:01:09  stage-3                done  pdfs=20 dir=course/materials/gnc-plane-3day-pilot
2026-04-27 08:02:18  stage-4                done  summary=course/orchestration/gnc-plane-3day-pilot/summary.md verdict=SHIPPABLE
2026-04-27 08:02:18  run                    end   wall-time=~7h subagent-spawns=~26 verdict=SHIPPABLE
2026-04-27 21:01:37  stage-3                rerun start material-builder-spawn reason=instructor-frame-overflow-fix
2026-04-27 21:17:41  stage-3                rerun done   pdfs=20 instructor-decks-grew=day1+5 day2+9 day3+4 reason=allowframebreaks-split-overflowed-frames
