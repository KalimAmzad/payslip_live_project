CREATE TABLE `member` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `full_name` varchar(255),
  `email` varchar(255),
  `dept` varchar(255),
  `status` varchar(255),
  `joining` datetime,
  `account_number` varchar(255),
  `gross_salary` numeric
);

CREATE TABLE `monthly_disbursement` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `date` datetime,
  `member_id` int,
  `basic` int,
  `home_rent_allowance` int,
  `conveyance_allowance` int,
  `medical_allowance` int,
  `study_attendence` int,
  `project_bonus` int,
  `referral_bonus` int,
  `eid_bonus` int,
  `kpi` int,
  `casual_leave` int,
  `overtime` int,
  `dearness_allowance` int,
  `csr_sale_bonus` int
);

CREATE TABLE `parameter` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `calculation_type` varchar(255)
);

ALTER TABLE `monthly_disbursement` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);
