from sqlalchemy import create_engine, Column, String, Text, Integer, DECIMAL, Date, ForeignKey, PrimaryKeyConstraint, CHAR
from sqlalchemy.orm import relationship, declarative_base
import os

Base = declarative_base()

class Occupation(Base):
    __tablename__ = 'Occupations'

    onet_soc_code = Column(String(20), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Relationship to Occupation_Skills (one-to-many)
    occupation_skills = relationship("OccupationSkill", back_populates="occupation")

class Skill(Base):
    __tablename__ = 'Skills'

    element_id = Column(String(20), primary_key=True, index=True)
    element_name = Column(String(255), nullable=False)

    # Relationship to Occupation_Skills (one-to-many)
    occupation_skills = relationship("OccupationSkill", back_populates="skill")

class OccupationSkill(Base):
    __tablename__ = 'Occupation_Skills'

    onet_soc_code = Column(String(20), ForeignKey('Occupations.onet_soc_code', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    element_id = Column(String(20), ForeignKey('Skills.element_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    scale_id = Column(String(10), index=True)
    data_value = Column(DECIMAL(5, 2))
    n_value = Column(Integer)
    standard_error = Column(DECIMAL(6, 4))
    lower_ci_bound = Column(DECIMAL(6, 4))
    upper_ci_bound = Column(DECIMAL(6, 4))
    recommend_suppress = Column(CHAR(1))
    not_relevant = Column(String(10))
    date_recorded = Column(Date)
    domain_source = Column(String(50))

    # Composite primary key definition
    __table_args__ = (
        PrimaryKeyConstraint('onet_soc_code', 'element_id', 'scale_id'),
        {}
    )

    # Relationships to Occupation and Skill (many-to-one)
    occupation = relationship("Occupation", back_populates="occupation_skills")
    skill = relationship("Skill", back_populates="occupation_skills")


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
    # This part is for basic verification if you run this file directly.
    # It doesn't create tables but shows how an engine could be made.
    print("SQLAlchemy schema definitions loaded.")
    print(f"Base.metadata.tables keys: {list(Base.metadata.tables.keys())}")
    try:
        # Attempt to create an engine just to check if env vars are loadable for it
        # Ensure env/env.env is sourced or variables are set for this direct run
        if not (os.getenv("MYSQL_USER") and os.getenv("MYSQL_PASSWORD") and os.getenv("MYSQL_DATABASE")):
            print("Cannot create test engine: MYSQL_USER, MYSQL_PASSWORD, or MYSQL_DATABASE environment variables are not set.")
        else:
            engine = get_sqlalchemy_engine()
            print(f"Successfully created a SQLAlchemy engine for: {engine.url}")
    except Exception as e:
        print(f"Error creating SQLAlchemy engine for testing: {e}") 