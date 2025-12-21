import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const storyAPI = {
    // GET /story - Fetch story from S3
    getStory: (bucket, objectKey) =>
        api.get('/story', { params: { bucket, object_key: objectKey } }),

    // POST /story - Upload story to S3
    uploadStory: (text, filepath, bucketName) =>
        api.post('/story', { text, filepath, bucket_name: bucketName }),
};

export const templateAPI = {
    // GET /templates - Get prompt templates
    getTemplate: (novelName, templateType) =>
        api.get('/templates', { params: { novel_name: novelName, template_type: templateType } }),
};

export const entityAPI = {
    // GET /similar_entities - Query similar entities
    getSimilarEntities: (queryText, nResults = 3) =>
        api.get('/similar_entities', { params: { query_text: queryText, n_results: nResults } }),

    // POST /entity - Add new entity
    addEntity: (entity, description, keyRelations, history) =>
        api.post('/entity', { entity, description, key_relations: keyRelations, history }),
};

export const generationAPI = {
    // GET /generate - Generate story continuation
    generateStory: (bucket, storyKey, novelName = 'first novel') =>
        api.get('/generate', { params: { bucket, story_key: storyKey, novel_name: novelName } }),
};

export const mineEntitiesAPI = {
    // POST /mine_entities - Mine entities from story text
    // This is a synchronous Lambda invocation that will block the frontend until it completes
    mineEntities: (storyText, novelName, username = 'default_user') =>
        api.post('/mine_entities', 
            { story_text: storyText, novel_name: novelName, username },
        ),
};

export default api;
