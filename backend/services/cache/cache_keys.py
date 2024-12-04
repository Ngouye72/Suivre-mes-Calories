"""
Définition des clés de cache pour l'application
"""

class CacheKeys:
    # Préfixes généraux
    USER_PREFIX = "user"
    MEAL_PREFIX = "meal"
    ANALYSIS_PREFIX = "analysis"
    PROFILE_PREFIX = "profile"
    WEATHER_PREFIX = "weather"
    SOCIAL_PREFIX = "social"
    
    @staticmethod
    def user_data(user_id):
        """Clé pour les données utilisateur"""
        return f"{CacheKeys.USER_PREFIX}:{user_id}:data"
    
    @staticmethod
    def user_profile(user_id):
        """Clé pour le profil utilisateur"""
        return f"{CacheKeys.PROFILE_PREFIX}:{user_id}"
    
    @staticmethod
    def user_meals(user_id, date=None):
        """Clé pour les repas d'un utilisateur"""
        if date:
            return f"{CacheKeys.MEAL_PREFIX}:{user_id}:{date.strftime('%Y-%m-%d')}"
        return f"{CacheKeys.MEAL_PREFIX}:{user_id}:all"
    
    @staticmethod
    def meal_detail(meal_id):
        """Clé pour les détails d'un repas"""
        return f"{CacheKeys.MEAL_PREFIX}:detail:{meal_id}"
    
    @staticmethod
    def nutrient_analysis(user_id, start_date, end_date):
        """Clé pour l'analyse nutritionnelle"""
        return (
            f"{CacheKeys.ANALYSIS_PREFIX}:nutrient:{user_id}:"
            f"{start_date.strftime('%Y-%m-%d')}:{end_date.strftime('%Y-%m-%d')}"
        )
    
    @staticmethod
    def behavior_analysis(user_id, start_date, end_date):
        """Clé pour l'analyse comportementale"""
        return (
            f"{CacheKeys.ANALYSIS_PREFIX}:behavior:{user_id}:"
            f"{start_date.strftime('%Y-%m-%d')}:{end_date.strftime('%Y-%m-%d')}"
        )
    
    @staticmethod
    def weather_impact(user_id, start_date, end_date):
        """Clé pour l'analyse de l'impact météo"""
        return (
            f"{CacheKeys.ANALYSIS_PREFIX}:weather:{user_id}:"
            f"{start_date.strftime('%Y-%m-%d')}:{end_date.strftime('%Y-%m-%d')}"
        )
    
    @staticmethod
    def circadian_analysis(user_id, days):
        """Clé pour l'analyse circadienne"""
        return f"{CacheKeys.ANALYSIS_PREFIX}:circadian:{user_id}:{days}"
    
    @staticmethod
    def seasonal_trends(user_id, year):
        """Clé pour les tendances saisonnières"""
        return f"{CacheKeys.ANALYSIS_PREFIX}:seasonal:{user_id}:{year}"
    
    @staticmethod
    def social_dining(user_id, start_date, end_date):
        """Clé pour l'analyse des repas sociaux"""
        return (
            f"{CacheKeys.ANALYSIS_PREFIX}:social:{user_id}:"
            f"{start_date.strftime('%Y-%m-%d')}:{end_date.strftime('%Y-%m-%d')}"
        )
    
    @staticmethod
    def weather_data(date):
        """Clé pour les données météo"""
        return f"{CacheKeys.WEATHER_PREFIX}:{date.strftime('%Y-%m-%d')}"
    
    @staticmethod
    def social_context(user_id, date):
        """Clé pour le contexte social"""
        return f"{CacheKeys.SOCIAL_PREFIX}:{user_id}:{date.strftime('%Y-%m-%d')}"
