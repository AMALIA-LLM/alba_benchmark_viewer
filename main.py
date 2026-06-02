from flask import Flask, render_template, request, jsonify, Response
import sqlite3
import os
import json

app = Flask(__name__)

def get_db():
    db_name = request.args.get('db', 'new_results.db')
    if not os.path.exists(db_name):
        db_name = 'new_results.db'
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    selected_db = request.args.get('db', 'new_results.db')
    
    # Route to evaluations view if evaluations.db is selected
    if selected_db == 'evaluations.db':
        return evaluations()

    # Route to conversations view if pt_pt_conversation_evaluations.db is selected
    if selected_db == 'pt_pt_conversation_evaluations.db':
        return conversations()

    # Route to amalia propor view
    if selected_db == 'amalia_propor.db':
        return amalia_propor()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get filter options
    models = cursor.execute('SELECT DISTINCT model_name FROM results ORDER BY model_name').fetchall()
    categories = cursor.execute('SELECT DISTINCT category FROM results ORDER BY category').fetchall()
    
    # Get filter parameters
    selected_model = request.args.get('model', '')
    selected_category = request.args.get('category', '')
    min_score = request.args.get('min_score', '')
    max_score = request.args.get('max_score', '')
    page = int(request.args.get('page', 1))
    
    # Get available databases
    dbs = [f for f in os.listdir('.') if f.endswith('.db')]
    
    # Build query
    query = 'SELECT * FROM results WHERE 1=1'
    params = []
    
    if selected_model:
        query += ' AND model_name = ?'
        params.append(selected_model)
    if selected_category:
        query += ' AND category = ?'
        params.append(selected_category)
    if min_score:
        query += ' AND score >= ?'
        params.append(float(min_score))
    if max_score:
        query += ' AND score <= ?'
        params.append(float(max_score))
    
    # Get total count and stats
    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    total_count = cursor.execute(count_query, params).fetchone()[0]
    
    stats_query = query.replace('SELECT *', 'SELECT AVG(score), MIN(score), MAX(score)')
    stats = cursor.execute(stats_query, params).fetchone()
    avg_score = round(stats[0], 2) if stats[0] else 0
    min_score_val = stats[1] if stats[1] else 0
    max_score_val = stats[2] if stats[2] else 0
    
    # Get median
    median_query = query.replace('SELECT *', 'SELECT score') + ' ORDER BY score'
    all_scores = [row[0] for row in cursor.execute(median_query, params).fetchall()]
    median_score = all_scores[len(all_scores)//2] if all_scores else 0
    
    # Pagination
    per_page = 50
    offset = (page - 1) * per_page
    total_pages = (total_count + per_page - 1) // per_page
    
    query += f' ORDER BY id DESC LIMIT {per_page} OFFSET {offset}'
    
    results = cursor.execute(query, params).fetchall()
    conn.close()
    
    return render_template('index.html', 
                         results=results, 
                         total_count=total_count,
                         page=page,
                         total_pages=total_pages,
                         models=models, 
                         categories=categories,
                         dbs=dbs,
                         selected_db=selected_db,
                         selected_model=selected_model,
                         selected_category=selected_category,
                         min_score=min_score,
                         max_score=max_score,
                         avg_score=avg_score,
                         median_score=median_score,
                         min_score_val=min_score_val,
                         max_score_val=max_score_val)

@app.route('/evaluations')
def evaluations():
    conn = sqlite3.connect('evaluations.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get filter options
    models = cursor.execute('SELECT DISTINCT model_name FROM evaluations ORDER BY model_name').fetchall()
    groups = cursor.execute('SELECT DISTINCT group_name FROM evaluations ORDER BY group_name').fetchall()
    
    # Get filter parameters
    selected_db = 'evaluations.db'
    selected_model = request.args.get('model', '')
    selected_group = request.args.get('group', '')
    min_score = request.args.get('min_score', '')
    max_score = request.args.get('max_score', '')
    page = int(request.args.get('page', 1))
    
    dbs = [f for f in os.listdir('.') if f.endswith('.db')]
    
    # Build query
    query = 'SELECT * FROM evaluations WHERE 1=1'
    params = []
    
    if selected_model:
        query += ' AND model_name = ?'
        params.append(selected_model)
    if selected_group:
        query += ' AND group_name = ?'
        params.append(selected_group)
    if min_score:
        query += ' AND score >= ?'
        params.append(float(min_score))
    if max_score:
        query += ' AND score <= ?'
        params.append(float(max_score))
    
    # Get total count and stats
    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    total_count = cursor.execute(count_query, params).fetchone()[0]
    
    stats_query = query.replace('SELECT *', 'SELECT AVG(score), MIN(score), MAX(score)')
    stats = cursor.execute(stats_query, params).fetchone()
    avg_score = round(stats[0], 2) if stats[0] else 0
    min_score_val = stats[1] if stats[1] else 0
    max_score_val = stats[2] if stats[2] else 0
    
    # Get median
    median_query = query.replace('SELECT *', 'SELECT score') + ' ORDER BY score'
    all_scores = [row[0] for row in cursor.execute(median_query, params).fetchall()]
    median_score = all_scores[len(all_scores)//2] if all_scores else 0
    
    # Pagination
    per_page = 50
    offset = (page - 1) * per_page
    total_pages = (total_count + per_page - 1) // per_page
    
    query += f' ORDER BY id DESC LIMIT {per_page} OFFSET {offset}'
    
    results = cursor.execute(query, params).fetchall()
    conn.close()
    
    return render_template('evaluations.html',
                         results=results,
                         total_count=total_count,
                         page=page,
                         total_pages=total_pages,
                         models=models,
                         groups=groups,
                         dbs=dbs,
                         selected_db=selected_db,
                         selected_model=selected_model,
                         selected_group=selected_group,
                         min_score=min_score,
                         max_score=max_score,
                         avg_score=avg_score,
                         median_score=median_score,
                         min_score_val=min_score_val,
                         max_score_val=max_score_val)

@app.route('/conversations')
def conversations():
    conn = sqlite3.connect('pt_pt_conversation_evaluations.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get filter options
    models = cursor.execute('SELECT DISTINCT model_name FROM evaluations ORDER BY model_name').fetchall()
    models = [dict(row) for row in models]
    conversations_list = cursor.execute('SELECT DISTINCT conversation_id FROM evaluations ORDER BY conversation_id').fetchall()
    conversations_list = [dict(row) for row in conversations_list]
    prompt_types = cursor.execute('SELECT DISTINCT prompt_type FROM evaluations ORDER BY prompt_type').fetchall()
    prompt_types = [dict(row) for row in prompt_types]

    # Get filter parameters
    selected_db = 'pt_pt_conversation_evaluations.db'
    selected_model = request.args.get('model', '')
    selected_conversation = request.args.get('conversation', '')
    selected_prompt_type = request.args.get('prompt_type', '')
    selected_show_raw = request.args.get('show_raw', '')
    show_raw = True if str(selected_show_raw).lower() in ('1', 'on', 'true') else False
    min_score = request.args.get('min_score', '')
    max_score = request.args.get('max_score', '')
    page = int(request.args.get('page', 1))
    
    dbs = [f for f in os.listdir('.') if f.endswith('.db')]
    
    # Build query
    query = 'SELECT * FROM evaluations WHERE 1=1'
    params = []
    
    if selected_model:
        query += ' AND model_name = ?'
        params.append(selected_model)
    if selected_conversation:
        query += ' AND conversation_id = ?'
        params.append(selected_conversation)
    if selected_prompt_type:
        query += ' AND prompt_type = ?'
        params.append(selected_prompt_type)
    if min_score:
        query += ' AND score >= ?'
        params.append(float(min_score))
    if max_score:
        query += ' AND score <= ?'
        params.append(float(max_score))
    
    # Get total count and stats
    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    total_count = cursor.execute(count_query, params).fetchone()[0]
    
    stats_query = query.replace('SELECT *', 'SELECT AVG(score), MIN(score), MAX(score)')
    stats = cursor.execute(stats_query, params).fetchone()
    avg_score = round(stats[0], 2) if stats[0] else 0
    min_score_val = stats[1] if stats[1] else 0
    max_score_val = stats[2] if stats[2] else 0
    
    # Get median
    median_query = query.replace('SELECT *', 'SELECT score') + ' ORDER BY score'
    all_scores = [row[0] for row in cursor.execute(median_query, params).fetchall()]
    median_score = all_scores[len(all_scores)//2] if all_scores else 0
    
    # Pagination
    per_page = 20
    offset = (page - 1) * per_page
    total_pages = (total_count + per_page - 1) // per_page
    
    query += f' ORDER BY conversation_id, turn_number LIMIT {per_page} OFFSET {offset}'
    
    results = cursor.execute(query, params).fetchall()
    
    # Convert results to dict
    results_with_names = [dict(row) for row in results]
    
    conn.close()
    return render_template('conversations.html',
                         results=results_with_names,
                         total_count=total_count,
                         page=page,
                         total_pages=total_pages,
                         models=models,
                         conversations_list=conversations_list,
                         prompt_types=prompt_types,
                         dbs=dbs,
                         selected_db=selected_db,
                         selected_model=selected_model,
                         selected_conversation=selected_conversation,
                         selected_prompt_type=selected_prompt_type,
                         show_raw=show_raw,
                         min_score=min_score,
                         max_score=max_score,
                         avg_score=avg_score,
                         median_score=median_score,
                         min_score_val=min_score_val,
                         max_score_val=max_score_val)

@app.route('/amalia_propor')
def amalia_propor():
    conn = sqlite3.connect('amalia_propor.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    models = cursor.execute('SELECT DISTINCT model_name FROM results ORDER BY model_name').fetchall()
    models = [dict(row) for row in models]
    categories = cursor.execute('SELECT DISTINCT category FROM results ORDER BY category').fetchall()
    categories = [dict(row) for row in categories]

    selected_db = 'amalia_propor.db'
    selected_model = request.args.get('model', '')
    selected_category = request.args.get('category', '')
    selected_show_judge = request.args.get('show_judge', '')
    show_judge = True if str(selected_show_judge).lower() in ('1', 'on', 'true') else False
    min_score = request.args.get('min_score', '')
    max_score = request.args.get('max_score', '')
    page = int(request.args.get('page', 1))

    dbs = [f for f in os.listdir('.') if f.endswith('.db')]

    query = 'SELECT * FROM results WHERE 1=1'
    params = []

    if selected_model:
        query += ' AND model_name = ?'
        params.append(selected_model)
    if selected_category:
        query += ' AND category = ?'
        params.append(selected_category)
    if min_score:
        query += ' AND score >= ?'
        params.append(float(min_score))
    if max_score:
        query += ' AND score <= ?'
        params.append(float(max_score))

    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    total_count = cursor.execute(count_query, params).fetchone()[0]

    stats_query = query.replace('SELECT *', 'SELECT AVG(score), MIN(score), MAX(score)')
    stats = cursor.execute(stats_query, params).fetchone()
    avg_score = round(stats[0], 2) if stats[0] else 0
    min_score_val = stats[1] if stats[1] else 0
    max_score_val = stats[2] if stats[2] else 0

    median_query = query.replace('SELECT *', 'SELECT score') + ' ORDER BY score'
    all_scores = [row[0] for row in cursor.execute(median_query, params).fetchall()]
    median_score = all_scores[len(all_scores)//2] if all_scores else 0

    per_page = 50
    offset = (page - 1) * per_page
    total_pages = (total_count + per_page - 1) // per_page

    query += f' ORDER BY id LIMIT {per_page} OFFSET {offset}'

    results = cursor.execute(query, params).fetchall()
    results = [dict(row) for row in results]
    conn.close()

    return render_template('amalia_propor.html',
                         results=results,
                         total_count=total_count,
                         page=page,
                         total_pages=total_pages,
                         models=models,
                         categories=categories,
                         dbs=dbs,
                         selected_db=selected_db,
                         selected_model=selected_model,
                         selected_category=selected_category,
                         show_judge=show_judge,
                         min_score=min_score,
                         max_score=max_score,
                         avg_score=avg_score,
                         median_score=median_score,
                         min_score_val=min_score_val,
                         max_score_val=max_score_val)


@app.route('/export_json')
def export_json():
    db_name = request.args.get('db', '')
    if not db_name or not os.path.exists(db_name):
        return jsonify({'error': 'Database not found'}), 404

    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if db_name == 'amalia_propor.db':
        query = 'SELECT * FROM results WHERE 1=1'
        params = []
        selected_model = request.args.get('model', '')
        selected_category = request.args.get('category', '')
        min_score = request.args.get('min_score', '')
        max_score = request.args.get('max_score', '')

        if selected_model:
            query += ' AND model_name = ?'
            params.append(selected_model)
        if selected_category:
            query += ' AND category = ?'
            params.append(selected_category)
        if min_score:
            query += ' AND score >= ?'
            params.append(float(min_score))
        if max_score:
            query += ' AND score <= ?'
            params.append(float(max_score))

        query += ' ORDER BY id'
        results = [dict(row) for row in cursor.execute(query, params).fetchall()]

    elif db_name == 'pt_pt_conversation_evaluations.db':
        query = 'SELECT * FROM evaluations WHERE 1=1'
        params = []
        selected_model = request.args.get('model', '')
        selected_conversation = request.args.get('conversation', '')
        selected_prompt_type = request.args.get('prompt_type', '')
        min_score = request.args.get('min_score', '')
        max_score = request.args.get('max_score', '')

        if selected_model:
            query += ' AND model_name = ?'
            params.append(selected_model)
        if selected_conversation:
            query += ' AND conversation_id = ?'
            params.append(selected_conversation)
        if selected_prompt_type:
            query += ' AND prompt_type = ?'
            params.append(selected_prompt_type)
        if min_score:
            query += ' AND score >= ?'
            params.append(float(min_score))
        if max_score:
            query += ' AND score <= ?'
            params.append(float(max_score))

        query += ' ORDER BY conversation_id, turn_number'
        rows = [dict(row) for row in cursor.execute(query, params).fetchall()]
        grouped = {}
        for row in rows:
            conv_id = row.get('conversation_id', 'unknown')
            if conv_id not in grouped:
                grouped[conv_id] = []
            grouped[conv_id].append(row)
        results = grouped

    elif db_name == 'evaluations.db':
        query = 'SELECT * FROM evaluations WHERE 1=1'
        params = []
        selected_model = request.args.get('model', '')
        selected_group = request.args.get('group', '')
        min_score = request.args.get('min_score', '')
        max_score = request.args.get('max_score', '')

        if selected_model:
            query += ' AND model_name = ?'
            params.append(selected_model)
        if selected_group:
            query += ' AND group_name = ?'
            params.append(selected_group)
        if min_score:
            query += ' AND score >= ?'
            params.append(float(min_score))
        if max_score:
            query += ' AND score <= ?'
            params.append(float(max_score))

        query += ' ORDER BY id'
        results = [dict(row) for row in cursor.execute(query, params).fetchall()]

    else:
        query = 'SELECT * FROM results ORDER BY id'
        results = [dict(row) for row in cursor.execute(query).fetchall()]

    conn.close()

    output = json.dumps(results, ensure_ascii=False, indent=2)
    return Response(
        output,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename={db_name.replace(".db", "")}_export.json'}
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
