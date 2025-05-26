-- Defines the schema for Occupations
CREATE TABLE Occupations (
    onet_soc_code VARCHAR(20) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Defines the schema for Skills
CREATE TABLE Skills (
    element_id VARCHAR(20) PRIMARY KEY,
    element_name VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Defines the schema for Occupation_Skills, linking Occupations to Skills with measurement data
CREATE TABLE Occupation_Skills (
    onet_soc_code VARCHAR(20),
    element_id VARCHAR(20),
    scale_id VARCHAR(10),
    data_value DECIMAL(5,2),
    n_value INT,
    standard_error DECIMAL(6,4),
    lower_ci_bound DECIMAL(6,4),
    upper_ci_bound DECIMAL(6,4),
    recommend_suppress CHAR(1),
    not_relevant VARCHAR(10),
    date_recorded DATE,
    domain_source VARCHAR(50),
    PRIMARY KEY (onet_soc_code, element_id, scale_id),
    FOREIGN KEY (onet_soc_code) REFERENCES Occupations(onet_soc_code) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (element_id) REFERENCES Skills(element_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 