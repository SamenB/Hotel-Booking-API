class DataMapper:
    """Base Data Mapper for ORM ↔ Schema transformation."""
    
    db_model = None
    schema = None
    
    @classmethod
    def map_to_schema(cls, model):
        """ORM model → Pydantic schema"""
        return cls.schema.model_validate(model, from_attributes=True)

    @classmethod
    def map_to_orm(cls, data):
        """Pydantic schema → ORM model"""
        return cls.db_model(**data.model_dump())