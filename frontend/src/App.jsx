import { useState } from 'react';
import { storyAPI, entityAPI, generationAPI } from './api';
import './index.css';

function App() {
  const [storyText, setStoryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [showEntityDialog, setShowEntityDialog] = useState(false);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);

  // Config for operations
  const [bucket, setBucket] = useState('');
  const [novelName, setNovelName] = useState('first novel');

  const handleGenerate = async () => {
    if (!storyText.trim()) {
      setMessage({ type: 'error', text: 'Please enter some story text first' });
      return;
    }

    if (!bucket) {
      setMessage({ type: 'error', text: 'Please set bucket name in menu' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // First, upload current story to S3
      const timestamp = Date.now();
      const storyKey = `temp/story-${timestamp}.txt`;

      await storyAPI.uploadStory(storyText, storyKey, bucket);

      // Generate continuation
      const response = await generationAPI.generateStory(bucket, storyKey, novelName);

      // Append continuation to the textbox
      setStoryText(storyText + '\n\n' + response.data.story_continuation);
      setMessage({ type: 'success', text: 'Story continuation generated!' });
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">NovelWriter</h1>
        <p className="app-subtitle">AI-Powered Story Completion</p>
      </header>

      <MenuBar
        onLoadStory={() => setShowLoadDialog(true)}
        onAddEntity={() => setShowEntityDialog(true)}
        onSettings={() => setShowSettingsDialog(true)}
      />

      {message && (
        <div className={`status-message status-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="editor-container">
        <textarea
          className="story-editor"
          value={storyText}
          onChange={(e) => setStoryText(e.target.value)}
          placeholder="Start writing your story here, or load an existing one from the menu..."
        />

        <div className="editor-footer">
          <div className="word-count">
            {storyText.split(/\s+/).filter(w => w.length > 0).length} words
          </div>
          <button
            className="btn btn-generate"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading" />
                Generating...
              </>
            ) : (
              <>
                ✨ Generate Continuation
              </>
            )}
          </button>
        </div>
      </div>

      {showLoadDialog && (
        <LoadStoryDialog
          onClose={() => setShowLoadDialog(false)}
          onLoad={(text) => {
            setStoryText(text);
            setShowLoadDialog(false);
            setMessage({ type: 'success', text: 'Story loaded successfully!' });
          }}
          bucket={bucket}
        />
      )}

      {showEntityDialog && (
        <AddEntityDialog
          onClose={() => setShowEntityDialog(false)}
          onAdd={() => {
            setShowEntityDialog(false);
            setMessage({ type: 'success', text: 'Entity added successfully!' });
          }}
        />
      )}

      {showSettingsDialog && (
        <SettingsDialog
          onClose={() => setShowSettingsDialog(false)}
          bucket={bucket}
          setBucket={setBucket}
          novelName={novelName}
          setNovelName={setNovelName}
        />
      )}
    </div>
  );
}

// Menu Bar Component
function MenuBar({ onLoadStory, onAddEntity, onSettings }) {
  return (
    <div className="menu-bar">
      <button className="menu-item" onClick={onLoadStory}>
        📂 Load Story
      </button>
      <button className="menu-item" onClick={onAddEntity}>
        🎭 Add Entity
      </button>
      <button className="menu-item" onClick={onSettings}>
        ⚙️ Settings
      </button>
    </div>
  );
}

// Load Story Dialog
function LoadStoryDialog({ onClose, onLoad, bucket }) {
  const [objectKey, setObjectKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLoad = async (e) => {
    e.preventDefault();

    if (!bucket) {
      setError('Please set bucket name in settings first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await storyAPI.getStory(bucket, objectKey);
      onLoad(response.data.content);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Load Story from S3</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleLoad}>
          <div className="form-group">
            <label className="form-label">Story Path (S3 Key)</label>
            <input
              type="text"
              className="form-input"
              value={objectKey}
              onChange={(e) => setObjectKey(e.target.value)}
              placeholder="stories/chapter-1.txt"
              required
              autoFocus
            />
          </div>

          {bucket && (
            <p className="text-muted">Loading from bucket: <strong>{bucket}</strong></p>
          )}

          {error && (
            <div className="status-message status-error">
              {error}
            </div>
          )}

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="loading" /> : 'Load Story'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Settings Dialog
function SettingsDialog({ onClose, bucket, setBucket, novelName, setNovelName }) {
  const handleSave = (e) => {
    e.preventDefault();
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Settings</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSave}>
          <div className="form-group">
            <label className="form-label">S3 Bucket</label>
            <input
              type="text"
              className="form-input"
              value={bucket}
              onChange={(e) => setBucket(e.target.value)}
              placeholder="my-story-bucket"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Novel Name</label>
            <input
              type="text"
              className="form-input"
              value={novelName}
              onChange={(e) => setNovelName(e.target.value)}
              placeholder="first novel"
            />
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Add Entity Dialog
function AddEntityDialog({ onClose, onAdd }) {
  const [entityName, setEntityName] = useState('');
  const [description, setDescription] = useState('');
  const [relations, setRelations] = useState('');
  const [history, setHistory] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await entityAPI.addEntity(entityName, description, relations, history);
      onAdd();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add Entity to ChromaDB</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Entity Name</label>
            <input
              type="text"
              className="form-input"
              value={entityName}
              onChange={(e) => setEntityName(e.target.value)}
              placeholder="Character or place name"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detailed description..."
              rows="3"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Key Relations</label>
            <input
              type="text"
              className="form-input"
              value={relations}
              onChange={(e) => setRelations(e.target.value)}
              placeholder="Relationships with other entities"
            />
          </div>

          <div className="form-group">
            <label className="form-label">History</label>
            <textarea
              className="form-textarea"
              value={history}
              onChange={(e) => setHistory(e.target.value)}
              placeholder="Background and history..."
              rows="3"
            />
          </div>

          {error && (
            <div className="status-message status-error">
              {error}
            </div>
          )}

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="loading" /> : 'Add Entity'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
