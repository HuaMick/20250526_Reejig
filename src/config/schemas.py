from sqlalchemy import create_engine, Column, String, Text, Integer, DECIMAL, Date, ForeignKey, PrimaryKeyConstraint, CHAR, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
import os
from typing import Dict

Base = declarative_base()

# O*NET Data Column Mappings (moved from extract_onet_data.py)
class OnetMappings:
    # Mapping dictionaries for O*NET data files
    OCCUPATIONS_COLUMN_RENAME_MAP: Dict[str, str] = {
        "O*NET-SOC Code": "onet_soc_code",
        "Title": "title",
        "Description": "description",
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
    onet_soc_code = Column(String(20), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    last_updated = Column(Date, nullable=False)

class Onet_Skills_API_landing(Base):
    __tablename__ = 'onet_skills_api_landing'

    onet_soc_code = Column(String(20), index=True)
    element_id = Column(String(20), index=True) # No longer primary key alone
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

class Onet_Scales_API_landing(Base):
    __tablename__ = 'onet_scales_api_landing'

    scale_id = Column(String(10), primary_key=True, index=True)
    scale_name = Column(String(255), nullable=False)
    minimum = Column(Integer)
    maximum = Column(Integer)

    # String columns for type handling
    string_columns = ['scale_id', 'scale_name']

    
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
    element_id = Column(String(20), index=True) # No longer primary key alone
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

    # Define unique constraint to prevent duplicates
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        # Adding a unique constraint on onet_soc_code and element_id
        # to prevent multiple proficiency entries for the same occupation-skill pair
        UniqueConstraint('onet_soc_code', 'element_id', name='uix_occupation_skill'),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_ai_ci"}
    )


# Example function to create an engine (can be used by other scripts)
# This helps centralize engine creation if needed, though mysql_init_tables will create its own.
def get_sqlalchemy_engine():
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_port = os.getenv('MYSQL_PORT', '3306')
    db_user = os.getenv('MYSQL_USER')
    db_password = os.getenv('MYSQL_PASSWORD')
    db_name = os.getenv('MYSQL_DATABASE', 'onet_data')

    if not all([db_user, db_password, db_name]):
        raise ValueError("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE environment variables are required for SQLAlchemy engine.")

    engine_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(engine_url)
    return engine


if __name__ == '__main__':
    raise Exception("""
    You are trying to run a schema definition file. It is not designed to be executable.
    """)