document.addEventListener('DOMContentLoaded', function() {
    // Formulaire des objectifs
    const goalsForm = document.getElementById('goals-form');
    goalsForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            weight: document.getElementById('weight').value,
            height: document.getElementById('height').value,
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            activity_level: document.getElementById('activity').value,
            goal_type: document.getElementById('goal').value
        };
        
        try {
            const response = await fetch('/calculate_goals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            // Afficher les objectifs
            document.getElementById('goals-display').style.display = 'block';
            document.getElementById('calorie-goal').textContent = data.calorie_goal;
            document.getElementById('protein-goal').textContent = data.protein_goal;
            document.getElementById('carb-goal').textContent = data.carb_goal;
            document.getElementById('fat-goal').textContent = data.fat_goal;
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue lors du calcul des objectifs');
        }
    });
    
    // Formulaire des repas
    const mealForm = document.getElementById('meal-form');
    mealForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            meal_type: document.getElementById('meal-type').value,
            food_name: document.getElementById('food-name').value,
            calories: document.getElementById('calories').value
        };
        
        try {
            const response = await fetch('/log_meal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Repas ajouté avec succès !');
                mealForm.reset();
            } else {
                alert('Erreur lors de l\'ajout du repas');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue lors de l\'ajout du repas');
        }
    });
});
