USE freeclass;

-- ====================
-- Building Groups 初始化
-- ====================
INSERT INTO building_groups (id, name, description) VALUES
(1, 'Group A', '7号楼A区、图书馆、综合楼、室外教学区域'),
(2, 'Group B', '7号楼B区、7号楼C区、3号楼、5号楼、8号楼')
ON DUPLICATE KEY UPDATE name=name;
-- ---------------------------------------------------

-- ====================
-- Sections 初始化
-- ====================
INSERT INTO sections (id, code, description) VALUES
(1, '0102', '第一、第二节课'),
(2, '0304', '第三、第四节课'),
(3, '0506', '第五、第六节课'),
(4, '0708', '第七、第八节课'),
(5, '0910', '第九、第十节课'),
(6, '1112', '第十一、第十二节课')
ON DUPLICATE KEY UPDATE code=code;
-- ---------------------------------------------------

-- ====================
-- Section Times Group A
-- ====================
INSERT INTO section_times (section_id, group_id, start_time, end_time) VALUES
(1, 1, '08:30:00', '10:10:00'),
(2, 1, '10:30:00', '12:10:00'),
(3, 1, '14:30:00', '16:10:00'),
(4, 1, '16:25:00', '18:05:00'),
(5, 1, '19:30:00', '21:10:00'),
(6, 1, '21:20:00', '22:05:00')
ON DUPLICATE KEY UPDATE start_time=start_time;
-- ---------------------------------------------------

-- ====================
-- Section Times Group B
-- ====================
INSERT INTO section_times (section_id, group_id, start_time, end_time) VALUES
(1, 2, '08:30:00', '10:15:00'),
(2, 2, '10:50:00', '12:30:00'),
(3, 2, '14:30:00', '16:10:00'),
(4, 2, '16:25:00', '18:05:00'),
(5, 2, '19:30:00', '21:10:00'),
(6, 2, '21:20:00', '22:05:00')
ON DUPLICATE KEY UPDATE start_time=start_time;
-- ---------------------------------------------------

-- ====================
-- Tags 初始化
-- ====================
INSERT INTO tags (id, name) VALUES
(1, '自习'),
(2, '四六级备考'),
(3, '小组讨论'),
(4, '朗诵练习'),
(5, '演讲排练'),
(6, '团队会议')
ON DUPLICATE KEY UPDATE name=name;
