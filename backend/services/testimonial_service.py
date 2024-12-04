from datetime import datetime
from models import User, db
import random

class TestimonialService:
    def __init__(self, user_id=None):
        self.user = User.query.get(user_id) if user_id else None

    def create_testimonial(self, data):
        """Crée un nouveau témoignage"""
        testimonial = {
            'user_id': self.user.id,
            'username': self.user.username,
            'title': data.get('title'),
            'content': data.get('content'),
            'initial_weight': data.get('initial_weight'),
            'current_weight': data.get('current_weight'),
            'time_period': data.get('time_period'),
            'tips': data.get('tips', []),
            'photos': data.get('photos', []),
            'date': datetime.now(),
            'likes': 0,
            'comments': [],
            'verified': False
        }

        # Calculer les statistiques
        if testimonial['initial_weight'] and testimonial['current_weight']:
            testimonial['weight_loss'] = testimonial['initial_weight'] - testimonial['current_weight']
            testimonial['success_rate'] = min(100, (testimonial['weight_loss'] / testimonial['initial_weight']) * 100)
        
        return testimonial

    def get_featured_testimonials(self, count=5):
        """Retourne les témoignages mis en avant"""
        # Simulation de témoignages (à remplacer par une vraie base de données)
        sample_testimonials = [
            {
                'user_id': 1,
                'username': 'Sophie',
                'title': 'Ma transformation en 6 mois',
                'content': """J'ai commencé mon parcours à 80kg, me sentant fatiguée et démotivée. 
                Grâce à cette application, j'ai appris à mieux gérer mon alimentation et à faire de 
                l'exercice régulièrement. Aujourd'hui, je pèse 65kg et je me sens en pleine forme !""",
                'initial_weight': 80,
                'current_weight': 65,
                'weight_loss': 15,
                'time_period': '6 mois',
                'success_rate': 18.75,
                'tips': [
                    'Prenez des photos régulièrement pour suivre votre progression',
                    'Planifiez vos repas à l\'avance',
                    'Ne vous découragez pas si la balance ne bouge pas pendant quelques jours'
                ],
                'likes': 245,
                'verified': True
            },
            {
                'user_id': 2,
                'username': 'Thomas',
                'title': 'Du sport et une meilleure alimentation',
                'content': """Ancien sportif ayant arrêté toute activité, j'avais pris beaucoup de 
                poids. Cette application m'a aidé à retrouver une alimentation équilibrée et à me 
                remettre progressivement au sport. -20kg en 8 mois !""",
                'initial_weight': 95,
                'current_weight': 75,
                'weight_loss': 20,
                'time_period': '8 mois',
                'success_rate': 21.05,
                'tips': [
                    'Commencez doucement avec le sport',
                    'Buvez beaucoup d\'eau',
                    'Évitez les régimes trop restrictifs'
                ],
                'likes': 189,
                'verified': True
            },
            {
                'user_id': 3,
                'username': 'Marie',
                'title': 'Perte de poids post-grossesse',
                'content': """Après ma grossesse, j'avais du mal à perdre les kilos en trop. 
                L'application m'a aidée à retrouver mon poids d'avant en respectant mon corps et 
                sans me priver.""",
                'initial_weight': 75,
                'current_weight': 62,
                'weight_loss': 13,
                'time_period': '10 mois',
                'success_rate': 17.33,
                'tips': [
                    'Soyez patient(e) avec votre corps',
                    'Privilégiez les aliments nutritifs',
                    'Faites-vous plaisir de temps en temps'
                ],
                'likes': 312,
                'verified': True
            }
        ]
        
        return sorted(sample_testimonials, key=lambda x: x['likes'], reverse=True)[:count]

    def get_success_stories(self, category=None):
        """Retourne les histoires de réussite filtrées par catégorie"""
        stories = self.get_featured_testimonials()
        
        if category:
            if category == 'weight_loss':
                stories = [s for s in stories if s['weight_loss'] > 10]
            elif category == 'quick_results':
                stories = [s for s in stories if 'mois' in s['time_period'] and int(s['time_period'].split()[0]) <= 6]
            elif category == 'maintenance':
                stories = [s for s in stories if s['success_rate'] > 15]
        
        return stories

    def get_tips_by_category(self, category):
        """Retourne des conseils personnalisés par catégorie"""
        all_tips = {
            'debutant': [
                'Commencez par tenir un journal alimentaire pendant une semaine',
                'Fixez-vous des objectifs réalistes et atteignables',
                'Pesez-vous une fois par semaine, pas plus',
                'Buvez au moins 1,5L d\'eau par jour',
                'Évitez les régimes restrictifs'
            ],
            'motivation': [
                'Prenez des photos de votre progression',
                'Célébrez les petites victoires',
                'Rejoignez la communauté pour du soutien',
                'Variez vos activités physiques',
                'Partagez vos succès avec d\'autres'
            ],
            'nutrition': [
                'Privilégiez les aliments complets',
                'Mangez beaucoup de légumes',
                'Évitez les aliments transformés',
                'Planifiez vos repas à l\'avance',
                'Écoutez votre corps et ses signaux de faim'
            ],
            'sport': [
                'Commencez doucement',
                'Trouvez une activité que vous aimez',
                'Alternez cardio et renforcement',
                'Étirez-vous après chaque séance',
                'Restez régulier dans vos activités'
            ]
        }
        
        return all_tips.get(category, [])

    def add_comment(self, testimonial_id, comment_data):
        """Ajoute un commentaire à un témoignage"""
        comment = {
            'user_id': self.user.id,
            'username': self.user.username,
            'content': comment_data['content'],
            'date': datetime.now(),
            'likes': 0
        }
        
        return comment

    def like_testimonial(self, testimonial_id):
        """Ajoute un like à un témoignage"""
        # À implémenter avec la base de données
        pass
