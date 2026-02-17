#!/usr/bin/env python3
"""
Frontend Flask pour le système RAG
Interface moderne et pratique pour interagir avec RAG_tools.py
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import threading

# Ajouter le dossier code au path pour importer RAG_tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))
from RAG_tools import RAG_Upload, RAG_Delete, RAG_Answer

import ollama
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_rag_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
BDD_FOLDER = 'bdd/rag'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BDD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Configuration RAG
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen3:0.6b-q4_K_M"

# Initialisation de ChromaDB
embedding_function = OllamaEmbeddingFunction(
    model_name=EMBEDDING_MODEL,
    url="http://localhost:11434/api/embeddings",
)

client = chromadb.PersistentClient(path=BDD_FOLDER)
chroma_collection = client.get_or_create_collection(
    "rag",
    embedding_function=embedding_function,
    configuration={"hnsw": {"space": "cosine"}}
)

# Stockage de l'historique des conversations (en mémoire)
conversation_history = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Page d'accueil avec l'interface de chat"""
    return render_template('chat.html')

@app.route('/upload')
def upload_page():
    """Page d'upload de documents"""
    return render_template('upload.html')

@app.route('/documents')
def documents_page():
    """Page de gestion des documents"""
    try:
        rag_delete = RAG_Delete(chroma_collection)
        files = rag_delete.get_files_saved()
        # Supprimer les doublons et les chaînes vides
        files = list(set([f for f in files if f and len(f) > 1]))
    except Exception as e:
        files = []
        flash(f'Erreur lors du chargement des documents: {str(e)}', 'error')
    
    return render_template('documents.html', documents=files)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint API pour le chat RAG"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Récupérer l'historique de la session
        history = conversation_history.get(session_id, [])
        
        # Créer l'instance RAG_Answer
        rag_answer = RAG_Answer(chroma_collection, llm=LLM_MODEL)
        
        # Obtenir la réponse
        stream, files = rag_answer.rag_stack(message, history)
        
        # Collecter la réponse complète
        full_response = ""
        for chunk in stream:
            full_response += chunk['message']['content']
        
        # Mettre à jour l'historique
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': full_response})
        conversation_history[session_id] = history[-10:]  # Garder les 10 derniers échanges
        
        return jsonify({
            'response': full_response,
            'sources': files,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint API pour l'upload de fichiers"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filepath)
        
        if not uploaded_files:
            return jsonify({'error': 'Aucun fichier valide (PDF uniquement)'}), 400
        
        # Indexation des fichiers dans un thread séparé
        def index_files():
            try:
                rag_upload = RAG_Upload(
                    chroma_collection, 
                    embeding_model=EMBEDDING_MODEL,
                    chunk_size=512,
                    overlap_size=128
                )
                rag_upload.stack(uploaded_files)
            except Exception as e:
                print(f"Erreur d'indexation: {e}")
        
        thread = threading.Thread(target=index_files)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} fichier(s) uploadé(s) et en cours d\'indexation',
            'files': [os.path.basename(f) for f in uploaded_files]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Endpoint API pour lister les documents"""
    try:
        rag_delete = RAG_Delete(chroma_collection)
        files = rag_delete.get_files_saved()
        files = list(set([f for f in files if f and len(f) > 1]))
        
        # Obtenir des statistiques
        stats = chroma_collection.count()
        
        return jsonify({
            'documents': files,
            'count': len(files),
            'total_chunks': stats,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/delete', methods=['POST'])
def delete_documents():
    """Endpoint API pour supprimer des documents"""
    try:
        data = request.get_json()
        files_to_delete = data.get('files', [])
        
        if not files_to_delete:
            return jsonify({'error': 'Aucun fichier spécifié'}), 400
        
        # Récupérer tous les fichiers actuels
        rag_delete = RAG_Delete(chroma_collection)
        all_files = rag_delete.get_files_saved()
        
        # Filtrer pour garder seulement les fichiers à conserver
        files_to_keep = [f for f in all_files if f not in files_to_delete]
        
        # Supprimer de la base de données
        rag_delete.remove_data(files_to_keep)
        
        return jsonify({
            'success': True,
            'message': f'{len(files_to_delete)} document(s) supprimé(s)',
            'deleted': files_to_delete
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint API pour les statistiques"""
    try:
        count = chroma_collection.count()
        rag_delete = RAG_Delete(chroma_collection)
        files = rag_delete.get_files_saved()
        files = [f for f in files if f and len(f) > 1]
        
        return jsonify({
            'total_chunks': count,
            'total_documents': len(set(files)),
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 RAG Web Interface")
    print("=" * 60)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🗄️  Database: {BDD_FOLDER}")
    print(f"🤖 LLM Model: {LLM_MODEL}")
    print(f"📊 Embedding: {EMBEDDING_MODEL}")
    print("=" * 60)
    print("🌐 Ouvrez http://localhost:5000 dans votre navigateur")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)