import os
from typing import Dict
from sqlalchemy import create_engine, Column, String, Text, Integer, DECIMAL, Date, DateTime, ForeignKey, PrimaryKeyConstraint, CHAR, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# O*NET Data Column Mappings
class OnetMappings:
    # Mapping dictionaries for O*NET data files (original text files)
    OCCUPATIONS_COLUMN_RENAME_MAP: Dict[str, str] = {
        "O*NET-SOC Code": "onet_soc_code",
        "Title": "title",
        "Description": "description",
    }

    # Mapping for O*NET API Occupation data (after pd.read_xml)
    API_OCCUPATIONS_COLUMN_RENAME_MAP: Dict[str, str] = {
        "onetsoc_code": "onet_soc_code", # API XML tag <onetsoc_code> becomes column 'onetsoc_code'
        # 'title' and 'description' usually match, but can be added if they differ from schema expectations
    }

    SKILLS_COLUMN_RENAME_MAP: Dict[str, str] = {
        "Element ID": "element_id",
        "Element Name": "element_name",
        "O*NET-SOC Code": "onet_soc_code",
        "Scale ID": "scale_id",
        "Data Value": "data_value",
        "N": "n_value",
        "Standard Error": "standard_error",
        "Lower CI Bound": "lower_ci_bound",
        "Upper CI Bound": "upper_ci_bound",
        "Recommend Suppress": "recommend_suppress",
        "Not Relevant": "not_relevant",
        "Date": "date_recorded",
        "Domain Source": "domain_source"
    }

    SCALES_COLUMN_RENAME_MAP: Dict[str, str] = {
        "Scale ID": "scale_id",
        "Scale Name": "scale_name",
        "Minimum": "minimum",
        "Maximum": "maximum"
    }

class Onet_Occupations_API_landing(Base):
    __tablename__ = 'onet_occupations_api_landing'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    onet_soc_code = Column(String(20), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    last_updated = Column(Date, nullable=False)

class Onet_Skills_API_landing(Base):
    __tablename__ = 'onet_skills_api_landing'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    onetsoc_code = Column(String(20), index=True, nullable=True)
    element_id = Column(String(20), index=True, nullable=False)
    element_name = Column(String(255), nullable=False)
    scale_id = Column(String(10), index=True, nullable=True)
    scale_name = Column(String(255), nullable=True)
    data_value = Column(DECIMAL(10, 2), nullable=True)
    importance = Column(DECIMAL(10, 2), nullable=True)
    level = Column(DECIMAL(10, 2), nullable=True)
    n_value = Column(Integer, nullable=True)
    standard_error = Column(DECIMAL(10, 4), nullable=True)
    lower_ci_bound = Column(DECIMAL(10, 4), nullable=True)
    upper_ci_bound = Column(DECIMAL(10, 4), nullable=True)
    recommend_suppress = Column(String(1), nullable=True)
    not_relevant = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    domain_source = Column(String(50), nullable=True)
    onet_update_date = Column(Date, nullable=True)
    last_updated = Column(Date, nullable=False)

    # String columns for type handling
    string_columns = ['onetsoc_code', 'element_id', 'element_name', 'scale_id', 'scale_name', 'recommend_suppress', 'not_relevant', 'domain_source']

    
class Onet_Occupations_Landing(Base):
    __tablename__ = 'onet_occupations_landing'

    onet_soc_code = Column(String(20), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # String columns for type handling
    string_columns = ['onet_soc_code', 'title', 'description']

    # Relationship to Occupation_Skills (one-to-many)
    # occupation_skills = relationship("OccupationSkill", back_populates="occupation", cascade="all, delete-orphan") # Removed

class Onet_Skills_Landing(Base):
    __tablename__ = 'onet_skills_landing'

    onet_soc_code = Column(String(20), index=True)
    element_id = Column(String(20), index=True)
    element_name = Column(String(255), nullable=False)
    scale_id = Column(String(10), index=True)
    data_value = Column(DECIMAL(5, 2), nullable=True)
    n_value = Column(Integer, nullable=True)
    standard_error = Column(DECIMAL(6, 4), nullable=True)
    lower_ci_bound = Column(DECIMAL(6, 4), nullable=True)
    upper_ci_bound = Column(DECIMAL(6, 4), nullable=True)
    recommend_suppress = Column(CHAR(1), nullable=True)
    not_relevant = Column(String(10), nullable=True)
    date_recorded = Column(Date, nullable=True)
    domain_source = Column(String(50), nullable=True)

    # String columns for type handling
    string_columns = ['element_id', 'element_name']

    # Composite primary key definition
    __table_args__ = (
        PrimaryKeyConstraint('onet_soc_code', 'element_id', 'scale_id'),
        {}
    )

class Onet_Scales_Landing(Base):
    __tablename__ = 'onet_scales_landing'

    scale_id = Column(String(10), primary_key=True, index=True)
    scale_name = Column(String(255), nullable=False)
    minimum = Column(Integer)
    maximum = Column(Integer)

    # String columns for type handling
    string_columns = ['scale_id', 'scale_name']


# Downstream normalized tables
class Skills(Base):
    __tablename__ = 'skills'

    element_id = Column(String(20), primary_key=True, index=True)
    element_name = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False)  # 'text_file', 'api', or 'merged'
    last_updated = Column(Date, nullable=False)


class Occupation_Skills(Base):
    __tablename__ = 'occupation_skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    onet_soc_code = Column(String(20), index=True, nullable=False)
    element_id = Column(String(20), index=True, nullable=False)
    proficiency_level = Column(DECIMAL(5, 2), nullable=False)
    source = Column(String(50), nullable=False)  # 'text_file', 'api', or 'merged'
    last_updated = Column(Date, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('onet_soc_code', 'element_id', name='uix_occupation_skill'),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_ai_ci"}
    )

class LLM_Skill_Proficiency_Requests(Base):
    __tablename__ = 'llm_skill_proficiency_requests'
    request_id = Column(String(36), index=True, nullable=False)
    request_model = Column(String(255), nullable=False)
    request_onet_soc_code = Column(String(20), index=True, nullable=False)
    request_skill_element_id = Column(String(20), index=True, nullable=False)
    request_skill_name = Column(String(255), nullable=False)
    request_timestamp = Column(DateTime, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('request_id', 'request_onet_soc_code', 'request_skill_element_id', name='pk_llm_skill_proficiency_requests'),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_ai_ci"}
    )

class LLM_Skill_Proficiency_Replies(Base):
    """
    Will store LLM responses for skill proficiency levels. 
    Responses can duplicate if the LLM is asked to assess the same skill for the same occupation.
    """
    __tablename__ = 'llm_skill_proficiency_replies'

    request_id = Column(String(36), index=True, nullable=False)
    llm_onet_soc_code = Column(String(20), index=True, nullable=False)
    llm_occupation_name = Column(String(255), nullable=False)
    llm_skill_name = Column(String(255), nullable=False)
    llm_assigned_proficiency_description = Column(String(255), nullable=True)
    llm_assigned_proficiency_level = Column(Integer, nullable=True)
    llm_explanation = Column(Text, nullable=True)
    assessment_timestamp = Column(DateTime, nullable=False) # Assuming DateTime is imported, similar to Date

    __table_args__ = (
        PrimaryKeyConstraint('request_id', 'llm_onet_soc_code', 'llm_skill_name', name='pk_llm_skill_proficiency_replies'),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_ai_ci"}
    )

# For testing use the test_env variables which can be found in the env/test_env.env file
def get_sqlalchemy_engine(
    db_name: str = 'onet_data',
    db_user: str = 'mysql-user',
    db_password: str = '2222',
    db_host: str = 'localhost',
    db_port: str = '3306'
):
    # Determine effective configuration, prioritizing explicitly passed non-default parameters
    effective_host = db_host
    if db_host == 'localhost':  # Default for db_host
        effective_host = os.getenv('MYSQL_HOST', 'localhost')

    effective_port = db_port
    if db_port == '3306':  # Default for db_port
        effective_port = os.getenv('MYSQL_PORT', '3306')

    effective_user = db_user
    if db_user == 'mysql-user':  # Default for db_user
        effective_user = os.getenv('MYSQL_USER', 'mysql-user')

    effective_password = db_password
    if db_password == '2222':  # Default for db_password
        effective_password = os.getenv('MYSQL_PASSWORD', '2222')

    effective_db_name = db_name
    if db_name == 'onet_data':  # Default for db_name
        effective_db_name = os.getenv('MYSQL_DATABASE', 'onet_data')

    if not all([effective_user, effective_password, effective_db_name, effective_host, effective_port]):
        # Added effective_host and effective_port to the check
        raise ValueError(
            "MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, and MYSQL_PORT "
            "must all be effectively set (either by params or env vars) for SQLAlchemy engine."
        )

    engine_url = f"mysql+mysqlconnector://{effective_user}:{effective_password}@{effective_host}:{effective_port}/{effective_db_name}"
    engine = create_engine(engine_url)
    return engine


if __name__ == '__main__':
    raise Exception("""
    You are trying to run a schema definition file. It is not designed to be executable.
    """)