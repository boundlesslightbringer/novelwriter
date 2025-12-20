import { useState } from 'react';
import { storyAPI, entityAPI, generationAPI, mineEntitiesAPI } from './api';
import './index.css';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  UserPlus, 
  Search, 
  Settings, 
  Sparkles, 
  Loader2,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

function App() {
  const [storyText, setStoryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [showEntityDialog, setShowEntityDialog] = useState(false);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);
  const [showMineDialog, setShowMineDialog] = useState(false);

  // Config for operations
  const [bucket, setBucket] = useState('');
  const [novelName, setNovelName] = useState('first novel');
  const [storyName, setStoryName] = useState('');

  const handleGenerate = async () => {
    if (!storyText.trim()) {
      setMessage({ type: 'error', text: 'Please enter some story text first' });
      return;
    }

    if (!bucket) {
      setMessage({ type: 'error', text: 'Please set bucket name in settings' });
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

  const wordCount = storyText.split(/\s+/).filter(w => w.length > 0).length;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            NovelWriter
          </h1>
          <p className="text-muted-foreground">AI-Powered Story Completion</p>
          {(novelName || storyName) && (
            <div className="flex items-center justify-center gap-2 pt-2">
              {novelName && (
                <Badge variant="secondary" className="text-xs font-normal">
                  Novel: {novelName}
                </Badge>
              )}
              {storyName && (
                <Badge variant="secondary" className="text-xs font-normal">
                  {storyName}
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Menu Bar */}
        <MenuBar
          onLoadStory={() => setShowLoadDialog(true)}
          onAddEntity={() => setShowEntityDialog(true)}
          onMineEntities={() => setShowMineDialog(true)}
          onSettings={() => setShowSettingsDialog(true)}
        />

        {/* Status Message */}
        {message && (
          <div className={`flex items-center gap-2 p-4 rounded-lg border ${
            message.type === 'success' 
              ? 'bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400' 
              : 'bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle2 className="size-5" />
            ) : (
              <AlertCircle className="size-5" />
            )}
            <span>{message.text}</span>
          </div>
        )}

        {/* Editor Container */}
        <Card className="flex flex-col h-[calc(100vh-300px)]">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Story Editor</CardTitle>
                <CardDescription>
                  {storyName ? (
                    <>
                      <span className="font-medium">{storyName}</span>
                      {novelName && <span className="text-muted-foreground"> • {novelName}</span>}
                    </>
                  ) : (
                    <>
                      {novelName ? (
                        <span>{novelName}</span>
                      ) : (
                        'Start writing your story here, or load an existing one from the menu'
                      )}
                    </>
                  )}
                </CardDescription>
              </div>
              {(novelName || storyName) && (
                <div className="flex gap-2">
                  {novelName && (
                    <Badge variant="outline" className="text-xs">
                      Novel: {novelName}
                    </Badge>
                  )}
                  {storyName && (
                    <Badge variant="outline" className="text-xs">
                      Story: {storyName}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col min-h-0">
            <Textarea
              className="flex-1 resize-none font-serif text-base leading-relaxed"
              value={storyText}
              onChange={(e) => setStoryText(e.target.value)}
              placeholder="Once upon a time..."
            />
          </CardContent>
          <CardFooter className="flex justify-between items-center border-t pt-4">
            <div className="text-sm text-muted-foreground">
              {wordCount} words
            </div>
            <Button
              onClick={handleGenerate}
              disabled={loading}
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="size-4" />
                  Generate Continuation
                </>
              )}
            </Button>
          </CardFooter>
        </Card>

        {/* Dialogs */}
        <LoadStoryDialog
          open={showLoadDialog}
          onOpenChange={setShowLoadDialog}
          onLoad={(text) => {
            setStoryText(text);
            setShowLoadDialog(false);
            setMessage({ type: 'success', text: 'Story loaded successfully!' });
          }}
          bucket={bucket}
        />

        <AddEntityDialog
          open={showEntityDialog}
          onOpenChange={setShowEntityDialog}
          onAdd={() => {
            setShowEntityDialog(false);
            setMessage({ type: 'success', text: 'Entity added successfully!' });
          }}
        />

        <MineEntitiesDialog
          open={showMineDialog}
          onOpenChange={setShowMineDialog}
          storyText={storyText}
          novelName={novelName}
          onComplete={() => {
            setShowMineDialog(false);
            setMessage({ type: 'success', text: 'Story analyzed successfully!' });
          }}
        />

        <SettingsDialog
          open={showSettingsDialog}
          onOpenChange={setShowSettingsDialog}
          bucket={bucket}
          setBucket={setBucket}
          novelName={novelName}
          setNovelName={setNovelName}
          storyName={storyName}
          setStoryName={setStoryName}
        />
      </div>
    </div>
  );
}

// Menu Bar Component
function MenuBar({ onLoadStory, onAddEntity, onMineEntities, onSettings }) {
  return (
    <div className="flex gap-2 flex-wrap">
      <Button variant="outline" onClick={onLoadStory}>
        <FileText className="size-4" />
        Load Story
      </Button>
      <Button variant="outline" onClick={onAddEntity}>
        <UserPlus className="size-4" />
        Add Entity
      </Button>
      <Button variant="outline" onClick={onMineEntities}>
        <Search className="size-4" />
        Analyze Story
      </Button>
      <Button variant="outline" onClick={onSettings}>
        <Settings className="size-4" />
        Settings
      </Button>
    </div>
  );
}

// Load Story Dialog
function LoadStoryDialog({ open, onOpenChange, onLoad, bucket }) {
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
      onOpenChange(false);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Load Story from S3</AlertDialogTitle>
          <AlertDialogDescription>
            Enter the S3 key path for the story you want to load
          </AlertDialogDescription>
        </AlertDialogHeader>
        <form onSubmit={handleLoad}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="story-key">Story Path (S3 Key)</FieldLabel>
              <Input
                id="story-key"
                value={objectKey}
                onChange={(e) => setObjectKey(e.target.value)}
                placeholder="stories/chapter-1.txt"
                required
                autoFocus
              />
            </Field>

            {bucket && (
              <p className="text-sm text-muted-foreground">
                Loading from bucket: <strong>{bucket}</strong>
              </p>
            )}

            {error && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-sm">
                <AlertCircle className="size-4" />
                {error}
              </div>
            )}

            <AlertDialogFooter>
              <AlertDialogCancel type="button">Cancel</AlertDialogCancel>
              <AlertDialogAction type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  'Load Story'
                )}
              </AlertDialogAction>
            </AlertDialogFooter>
          </FieldGroup>
        </form>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// Settings Dialog
function SettingsDialog({ open, onOpenChange, bucket, setBucket, novelName, setNovelName, storyName, setStoryName }) {
  const handleSave = (e) => {
    e.preventDefault();
    onOpenChange(false);
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Settings</AlertDialogTitle>
          <AlertDialogDescription>
            Configure your S3 bucket, novel name, and current story/chapter name
          </AlertDialogDescription>
        </AlertDialogHeader>
        <form onSubmit={handleSave}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="bucket">S3 Bucket</FieldLabel>
              <Input
                id="bucket"
                value={bucket}
                onChange={(e) => setBucket(e.target.value)}
                placeholder="my-story-bucket"
                autoFocus
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="novel-name">Novel Name</FieldLabel>
              <Input
                id="novel-name"
                value={novelName}
                onChange={(e) => setNovelName(e.target.value)}
                placeholder="first novel"
              />
              <p className="text-xs text-muted-foreground mt-1">
                The name of your novel or book series
              </p>
            </Field>

            <Field>
              <FieldLabel htmlFor="story-name">Story/Chapter Name</FieldLabel>
              <Input
                id="story-name"
                value={storyName}
                onChange={(e) => setStoryName(e.target.value)}
                placeholder="Chapter 1, The Beginning, etc."
              />
              <p className="text-xs text-muted-foreground mt-1">
                The name of the current chapter or individual story within the novel
              </p>
            </Field>

            <AlertDialogFooter>
              <AlertDialogCancel type="button">Cancel</AlertDialogCancel>
              <AlertDialogAction type="submit">Save</AlertDialogAction>
            </AlertDialogFooter>
          </FieldGroup>
        </form>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// Add Entity Dialog
function AddEntityDialog({ open, onOpenChange, onAdd }) {
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
      onOpenChange(false);
      // Reset form
      setEntityName('');
      setDescription('');
      setRelations('');
      setHistory('');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-2xl">
        <AlertDialogHeader>
          <AlertDialogTitle>Add Entity to ChromaDB</AlertDialogTitle>
          <AlertDialogDescription>
            Add a new character, place, or other entity to your story database
          </AlertDialogDescription>
        </AlertDialogHeader>
        <form onSubmit={handleSubmit}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="entity-name">Entity Name</FieldLabel>
              <Input
                id="entity-name"
                value={entityName}
                onChange={(e) => setEntityName(e.target.value)}
                placeholder="Character or place name"
                required
                autoFocus
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="description">Description</FieldLabel>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Detailed description..."
                rows="3"
                required
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="relations">Key Relations</FieldLabel>
              <Input
                id="relations"
                value={relations}
                onChange={(e) => setRelations(e.target.value)}
                placeholder="Relationships with other entities"
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="history">History</FieldLabel>
              <Textarea
                id="history"
                value={history}
                onChange={(e) => setHistory(e.target.value)}
                placeholder="Background and history..."
                rows="3"
              />
            </Field>

            {error && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-sm">
                <AlertCircle className="size-4" />
                {error}
              </div>
            )}

            <AlertDialogFooter>
              <AlertDialogCancel type="button">Cancel</AlertDialogCancel>
              <AlertDialogAction type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  'Add Entity'
                )}
              </AlertDialogAction>
            </AlertDialogFooter>
          </FieldGroup>
        </form>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// Mine Entities Dialog
function MineEntitiesDialog({ open, onOpenChange, storyText, novelName, onComplete }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleMine = async () => {
    if (!storyText.trim()) {
      setError('Please enter some story text first');
      return;
    }

    if (!novelName.trim()) {
      setError('Please set a novel name in settings');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // This will wait synchronously for the Lambda function to complete
      // The backend invokes the Lambda with RequestResponse (synchronous) type
      const response = await mineEntitiesAPI.mineEntities(storyText, novelName);
      setResult(response.data);
      onComplete();
      // Don't close dialog immediately so user can see the result
    } catch (err) {
      // Handle timeout errors specifically
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        setError('Request timed out. The Lambda function may still be processing. Please try again.');
      } else {
        setError(err.response?.data?.detail || err.message || 'Failed to mine entities');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Analyze Story</AlertDialogTitle>
          <AlertDialogDescription>
            Extract entities (characters, places, etc.) from your story text.
            This process may take up to 5 minutes as it processes your story.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-sm">
              <AlertCircle className="size-4" />
              {error}
            </div>
          )}
          
          {result && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400 text-sm">
                <CheckCircle2 className="size-4" />
                <span>{result.message || 'Entities mined successfully!'}</span>
              </div>
              {result.result && (
                <div className="p-3 rounded-lg bg-muted border text-sm max-h-48 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-xs">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          <AlertDialogFooter>
            <AlertDialogCancel 
              type="button" 
              disabled={loading}
              onClick={() => {
                setError(null);
                setResult(null);
                onOpenChange(false);
              }}
            >
              {result ? 'Close' : 'Cancel'}
            </AlertDialogCancel>
            {!result && (
              <AlertDialogAction onClick={handleMine} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Search className="size-4" />
                    Analyze
                  </>
                )}
              </AlertDialogAction>
            )}
          </AlertDialogFooter>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
}

export default App;
