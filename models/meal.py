from database import db
from datetime import datetime, timedelta, timezone

class Meal(db.Model):
    """
    Modelo de refeição.
    Contém informações sobre a refeição, como nome (café da manhã, almoço, etc.), descrição, horário que foi feita e se está na dieta ou não.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80) , nullable=False)
    data_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    in_diet = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        # Converte para horário de Brasília (UTC-3)
        data_time_brasilia = self.data_time - timedelta(hours=3)

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "data_time": data_time_brasilia,
            "in_diet": self.in_diet
        }