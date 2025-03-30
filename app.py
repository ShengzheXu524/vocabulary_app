from flask import Flask, render_template, request, session, jsonify, redirect, url_for, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
# Set a secret key for session encryption and security
app.secret_key = os.urandom(24)

# Dictionary containing our 5 vocabulary words with their details
# Each word includes definition, example sentences, memory tips, and mastery level
VOCABULARY_WORDS = {
    "symphony": {
        "word": "Symphony",
        "definition": "An elaborate musical composition for full orchestra, typically in four movements.",
        "example": "The orchestra performed Beethoven's Ninth Symphony to a standing ovation.",
        "memory_tip": "Think of 'sym' (together) + 'phony' (sound) = sounds coming together in harmony.",
        "part_of_speech": "noun"
    },
    "capsule": {
        "word": "Capsule",
        "definition": "A small case or container, especially a round or cylindrical one.",
        "example": "The time capsule contained artifacts from the 21st century.",
        "memory_tip": "Visualize a small space 'cap'able of holding something in-'sule' (inside).",
        "part_of_speech": "noun"
    },
    "cunning": {
        "word": "Cunning",
        "definition": "Skill in achieving one's ends by deceit or evasion; craftiness.",
        "example": "The cunning fox managed to steal the chicken without being noticed.",
        "memory_tip": "Can be remembered as 'running a con' - con+ning = cunning.",
        "part_of_speech": "adjective"
    },
    "feisty": {
        "word": "Feisty",
        "definition": "Having or showing exuberance, strong determination, or combativeness.",
        "example": "Despite her age, my grandmother remains quite feisty and independent.",
        "memory_tip": "Think of a small dog with a 'fist-y' (fighting) attitude.",
        "part_of_speech": "adjective"
    },
    "scrape": {
        "word": "Scrape",
        "definition": "To drag or pull a hard or sharp implement across a surface to remove dirt or other matter.",
        "example": "He had to scrape ice off his car windshield on the cold winter morning.",
        "memory_tip": "The sound 'scrrrr' mimics the action of scraping something.",
        "part_of_speech": "verb"
    }
}

# Quiz questions for each word to test user knowledge
QUIZ_QUESTIONS = {
    "symphony": [
        {
            "question": "What is the primary definition of 'Symphony'?",
            "options": [
                "A type of wind instrument",
                "An elaborate musical composition for full orchestra",
                "A harmony of colors in art",
                "A group of musicians"
            ],
            "correct_answer": 1
        },
        {
            "question": "Which part of speech is 'Symphony'?",
            "options": ["Verb", "Adjective", "Noun", "Adverb"],
            "correct_answer": 2
        }
    ],
    "capsule": [
        {
            "question": "What best describes a 'Capsule'?",
            "options": [
                "A type of medicine",
                "A small case or container",
                "A space vehicle",
                "A summary of information"
            ],
            "correct_answer": 1
        },
        {
            "question": "In which sentence is 'Capsule' used correctly?",
            "options": [
                "He capsule the important documents.",
                "The capsule contained items from 100 years ago.",
                "She felt very capsule after the meeting.",
                "They capsule through the forest quickly."
            ],
            "correct_answer": 1
        }
    ],
    "cunning": [
        {
            "question": "Which word is closest in meaning to 'Cunning'?",
            "options": ["Honest", "Clever", "Simple", "Direct"],
            "correct_answer": 1
        },
        {
            "question": "What quality does 'Cunning' often imply?",
            "options": [
                "Physical strength",
                "Moral uprightness",
                "Deception or craftiness",
                "Educational achievement"
            ],
            "correct_answer": 2
        }
    ],
    "feisty": [
        {
            "question": "Which of these animals would most likely be described as 'Feisty'?",
            "options": [
                "A sleeping cat",
                "A docile sheep",
                "A small dog barking at larger dogs",
                "A slow-moving turtle"
            ],
            "correct_answer": 2
        },
        {
            "question": "What emotion or quality does 'Feisty' suggest?",
            "options": [
                "Calmness and tranquility",
                "Spirited determination or combativeness",
                "Sadness and melancholy",
                "Confusion and disorientation"
            ],
            "correct_answer": 1
        }
    ],
    "scrape": [
        {
            "question": "What action best represents 'Scrape'?",
            "options": [
                "To fold gently",
                "To cut entirely through",
                "To drag a hard implement across a surface",
                "To dissolve in liquid"
            ],
            "correct_answer": 2
        },
        {
            "question": "Which tool would you most likely use to 'Scrape' something?",
            "options": [
                "A sponge",
                "A spatula",
                "A hammer",
                "A paintbrush"
            ],
            "correct_answer": 1
        }
    ]
}

@app.route('/')
def index():
    """
    Main route that renders the homepage with all vocabulary words.
    Initializes session data for tracking word mastery if not already present.
    """
    # Initialize session data for tracking word mastery if not already present
    if 'word_progress' not in session:
        session['word_progress'] = {word: {"mastery": 0, "last_studied": None} for word in VOCABULARY_WORDS}
    
    # Get the list of words with their mastery levels
    words_with_progress = []
    for word_key, word_data in VOCABULARY_WORDS.items():
        word_info = {
            "key": word_key,
            "word": word_data["word"],
            "mastery": session['word_progress'][word_key]["mastery"],
            "last_studied": session['word_progress'][word_key]["last_studied"]
        }
        words_with_progress.append(word_info)
    
    return render_template('index.html', words=words_with_progress)

@app.route('/word/<word_key>')
def word_detail(word_key):
    """
    Route to display detailed information about a specific word.
    Updates the 'last_studied' timestamp for the word.
    
    Args:
        word_key (str): The key of the word to display
    """
    # Check if the word exists in our vocabulary
    if word_key not in VOCABULARY_WORDS:
        return redirect(url_for('index'))
    
    # Update last studied timestamp
    session['word_progress'][word_key]['last_studied'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session.modified = True
    
    word_data = VOCABULARY_WORDS[word_key]
    word_progress = session['word_progress'][word_key]
    
    return render_template(
        'word_detail.html',
        word_key=word_key,
        word=word_data,
        mastery=word_progress['mastery'],
        last_studied=word_progress['last_studied']
    )

@app.route('/quiz/<word_key>')
def quiz(word_key):
    """
    Route to display quiz questions for a specific word.
    
    Args:
        word_key (str): The key of the word to quiz on
    """
    # Check if the word exists in our vocabulary
    if word_key not in VOCABULARY_WORDS or word_key not in QUIZ_QUESTIONS:
        return redirect(url_for('index'))
    
    word_data = VOCABULARY_WORDS[word_key]
    quiz_data = QUIZ_QUESTIONS[word_key]
    
    return render_template(
        'quiz.html',
        word_key=word_key,
        word=word_data,
        quiz_questions=quiz_data
    )

@app.route('/update_mastery', methods=['POST'])
def update_mastery():
    """
    API endpoint to update the mastery level of a word based on quiz results.
    
    Expected POST data:
        word_key (str): The key of the word
        correct_answers (int): Number of correct answers
        total_questions (int): Total number of questions
    """
    data = request.get_json()
    word_key = data.get('word_key')
    correct_answers = data.get('correct_answers', 0)
    total_questions = data.get('total_questions', 0)
    
    # Validate input
    if word_key not in VOCABULARY_WORDS:
        return jsonify({"success": False, "error": "Invalid word key"}), 400
    
    # Calculate new mastery level (0-5 stars)
    # Each correct answer can add up to 2.5 stars (5 stars max for all correct)
    mastery_gain = (correct_answers / total_questions) * 5
    current_mastery = session['word_progress'][word_key]['mastery']
    
    # Mastery can only increase, not decrease, and is capped at 5
    new_mastery = min(5, max(current_mastery, mastery_gain))
    
    # Update session data
    session['word_progress'][word_key]['mastery'] = new_mastery
    session['word_progress'][word_key]['last_studied'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session.modified = True
    
    return jsonify({
        "success": True,
        "word_key": word_key,
        "new_mastery": new_mastery,
        "correct_answers": correct_answers,
        "total_questions": total_questions
    })

@app.route('/reset_progress', methods=['POST'])
def reset_progress():
    """
    API endpoint to reset all progress or progress for a single word.
    
    Expected POST data:
        word_key (str, optional): If provided, only reset this word's progress
    """
    data = request.get_json()
    word_key = data.get('word_key', None)
    
    if word_key:
        # Reset progress for a specific word
        if word_key in VOCABULARY_WORDS:
            session['word_progress'][word_key] = {"mastery": 0, "last_studied": None}
    else:
        # Reset progress for all words
        session['word_progress'] = {word: {"mastery": 0, "last_studied": None} for word in VOCABULARY_WORDS}
    
    session.modified = True
    
    return jsonify({"success": True})

@app.route('/journey')
def journey():
    """
    Initializes the learning journey mode.
    Sets up session variables to track journey progress and redirects to the first word.
    Only includes words that aren't fully mastered (less than 5 stars).
    """
    # Initialize session if needed
    if 'word_progress' not in session:
        session['word_progress'] = {word: {"mastery": 0, "last_studied": None} for word in VOCABULARY_WORDS}
    
    # Filter out words that have been fully mastered (5 stars)
    unmastered_words = [
        word_key for word_key in VOCABULARY_WORDS.keys() 
        if session['word_progress'][word_key]['mastery'] < 5
    ]
    
    # Check if there are any unmastered words
    if not unmastered_words:
        # All words are mastered!
        # In a real app, you might add a flash message here:
        # flash("Congratulations! You've mastered all words. Starting a new journey with all words.")
        
        # For this demo, let's just include all words if everything is mastered
        unmastered_words = list(VOCABULARY_WORDS.keys())
    
    # Initialize journey progress with only unmastered words
    session['journey_progress'] = {
        'current_word_index': 0,  # Index of current word in unmastered_words
        'current_state': 'learn',  # Either 'learn' or 'quiz'
        'words_completed': [],     # List of completed word keys
        'unmastered_words': unmastered_words,  # List of words to study
        'started_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save changes to session
    session.modified = True
    
    # Redirect to the first unmastered word's learning page
    if unmastered_words:
        current_word_key = unmastered_words[0]
        return redirect(url_for('journey_learn', word_key=current_word_key))
    else:
        # This shouldn't happen due to the earlier check, but just in case
        return redirect(url_for('index'))

@app.route('/journey/learn/<word_key>')
def journey_learn(word_key):
    """
    Displays the learning page for a specific word in the journey.
    Similar to word_detail but with journey-specific navigation.
    
    Args:
        word_key (str): The key of the word to learn
    """
    # Check if the word exists in our vocabulary
    if word_key not in VOCABULARY_WORDS:
        return redirect(url_for('journey'))
    
    # Update last studied timestamp
    session['word_progress'][word_key]['last_studied'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session.modified = True
    
    # Get word data
    word_data = VOCABULARY_WORDS[word_key]
    word_progress = session['word_progress'][word_key]
    journey_progress = session.get('journey_progress', {})
    
    # Update journey state
    journey_progress['current_state'] = 'learn'
    session.modified = True
    
    # Calculate journey progress percentage
    word_keys = journey_progress.get('unmastered_words', list(VOCABULARY_WORDS.keys()))
    total_steps = len(word_keys) * 2  # Each word has learn and quiz steps
    
    # Find the current word's index in our filtered list
    try:
        current_word_index = word_keys.index(word_key)
    except ValueError:
        current_word_index = 0
        
    journey_progress['current_word_index'] = current_word_index
    
    current_step = current_word_index * 2  # Two steps per word
    if journey_progress.get('current_state') == 'quiz':
        current_step += 1
    progress_percentage = (current_step / total_steps) * 100 if total_steps > 0 else 100
    
    return render_template(
        'journey_learn.html',
        word_key=word_key,
        word=word_data,
        mastery=word_progress['mastery'],
        last_studied=word_progress['last_studied'],
        journey_progress=journey_progress,
        progress_percentage=progress_percentage
    )

@app.route('/journey/quiz/<word_key>')
def journey_quiz(word_key):
    """
    Displays the quiz page for a specific word in the journey.
    Similar to the regular quiz but with journey-specific navigation and logic.
    
    Args:
        word_key (str): The key of the word to quiz on
    """
    # Check if the word exists and has quiz questions
    if word_key not in VOCABULARY_WORDS or word_key not in QUIZ_QUESTIONS:
        return redirect(url_for('journey'))
    
    # Get word and quiz data
    word_data = VOCABULARY_WORDS[word_key]
    quiz_data = QUIZ_QUESTIONS[word_key]
    journey_progress = session.get('journey_progress', {})
    
    # Update journey state
    journey_progress['current_state'] = 'quiz'
    session.modified = True
    
    # Calculate journey progress percentage
    word_keys = journey_progress.get('unmastered_words', list(VOCABULARY_WORDS.keys()))
    total_steps = len(word_keys) * 2  # Each word has learn and quiz steps
    
    # Find the current word's index in our filtered list
    try:
        current_word_index = word_keys.index(word_key)
    except ValueError:
        current_word_index = 0
        
    journey_progress['current_word_index'] = current_word_index
    
    current_step = current_word_index * 2 + 1  # Two steps per word, quiz is second step
    progress_percentage = (current_step / total_steps) * 100 if total_steps > 0 else 100
    
    return render_template(
        'journey_quiz.html',
        word_key=word_key,
        word=word_data,
        quiz_questions=quiz_data,
        journey_progress=journey_progress,
        progress_percentage=progress_percentage
    )

@app.route('/journey/next', methods=['POST'])
def journey_next():
    """
    Handles progression through the journey:
    - From learn to quiz for the same word
    - From quiz to learn for the next word (if quiz passed)
    - From quiz back to learn for the same word (if quiz failed)
    
    Expected POST data:
        word_key (str): Current word key
        direction (str): Either 'to_quiz' or 'from_quiz'
        quiz_passed (bool, optional): Whether the quiz was passed (only for 'from_quiz')
    """
    data = request.get_json()
    word_key = data.get('word_key')
    direction = data.get('direction')
    quiz_passed = data.get('quiz_passed', False)
    
    # Validate input
    if word_key not in VOCABULARY_WORDS:
        return jsonify({"success": False, "error": "Invalid word key"}), 400
    
    if direction not in ['to_quiz', 'from_quiz']:
        return jsonify({"success": False, "error": "Invalid direction"}), 400
    
    # Get journey progress
    journey_progress = session.get('journey_progress', {})
    
    if direction == 'to_quiz':
        # Move from learn to quiz for the same word
        return jsonify({
            "success": True,
            "redirect": url_for('journey_quiz', word_key=word_key)
        })
    
    elif direction == 'from_quiz':
        # Processing quiz results
        if quiz_passed:
            # Add word to completed words
            if word_key not in journey_progress.get('words_completed', []):
                journey_progress.setdefault('words_completed', []).append(word_key)
            
            # Get the filtered word list
            word_keys = journey_progress.get('unmastered_words', list(VOCABULARY_WORDS.keys()))
            
            # Find the index of the current word
            try:
                current_index = word_keys.index(word_key)
            except ValueError:
                # Word not in list, redirect to journey start
                return jsonify({
                    "success": True,
                    "redirect": url_for('journey')
                })
            
            # Check if this was the last word
            if current_index >= len(word_keys) - 1:
                # Journey completed!
                journey_progress['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                session.modified = True
                return jsonify({
                    "success": True,
                    "redirect": url_for('journey_complete')
                })
            else:
                # Move to the next word
                next_index = current_index + 1
                next_word = word_keys[next_index]
                journey_progress['current_word_index'] = next_index
                journey_progress['current_state'] = 'learn'
                session.modified = True
                return jsonify({
                    "success": True,
                    "redirect": url_for('journey_learn', word_key=next_word)
                })
        else:
            # Quiz failed, return to learning the same word
            return jsonify({
                "success": True,
                "redirect": url_for('journey_learn', word_key=word_key)
            })
    
    # If we got here, something went wrong
    return jsonify({"success": False, "error": "Invalid request"}), 400

@app.route('/journey/complete')
def journey_complete():
    """
    Displays the journey completion page.
    Shows a summary of the user's achievements, time taken, and mastery gained.
    """
    # Get journey progress
    journey_progress = session.get('journey_progress', {})
    
    # Check if journey is actually complete
    if len(journey_progress.get('words_completed', [])) < len(journey_progress.get('unmastered_words', [])):
        return redirect(url_for('journey'))
    
    # Calculate statistics for the completion page
    started_at = journey_progress.get('started_at')
    completed_at = journey_progress.get('completed_at')
    
    # Calculate time difference if both timestamps exist
    time_taken = None
    if started_at and completed_at:
        start_time = datetime.strptime(started_at, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(completed_at, "%Y-%m-%d %H:%M:%S")
        time_diff = end_time - start_time
        # Format as hours, minutes, seconds
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_taken = f"{hours}h {minutes}m {seconds}s"
    
    # Get mastery levels for all words
    word_mastery = {}
    for word_key in VOCABULARY_WORDS:
        word_mastery[word_key] = {
            "word": VOCABULARY_WORDS[word_key]["word"],
            "mastery": session['word_progress'][word_key]["mastery"]
        }
    
    # Calculate average mastery
    total_mastery = sum(info["mastery"] for info in word_mastery.values())
    avg_mastery = total_mastery / len(word_mastery) if word_mastery else 0
    
    return render_template(
        'journey_complete.html',
        journey_progress=journey_progress,
        word_mastery=word_mastery,
        time_taken=time_taken,
        avg_mastery=avg_mastery
    )

if __name__ == '__main__':
    app.run(debug=True)