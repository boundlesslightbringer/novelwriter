
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel


class TextCompletionPromptTemplate(BaseModel):
    novel_name: str
    template_type: str
    prompt_template: str
    date: datetime 
    version: float
    
# Create a DynamoDB client using the default credentials and region
dynamodb = boto3.client("dynamodb")
# Get a resource object
dynamodb_resource = boto3.resource("dynamodb")

# Get the table
prompt_templates_table = dynamodb_resource.Table('PromptTemplates')

def insert_template(item: TextCompletionPromptTemplate, table) -> bool:
    """
    Inserts an item into the PromptTemplates DynamoDB table.

    :param item: A TextCompletionPromptTemplate object.
    :return: True if the item was inserted successfully, False otherwise.
    """
    try:
        response = table.put_item(
            Item={
                'novel_name': item.novel_name,
                'template_type': item.template_type,
                'prompt_template': item.prompt_template,
                'date': item.date.strftime("%d-%m-%Y"),
                'version': str(item.version)
            }
        )
        print(f"Successfully inserted item. Response: {response}")
        return True
    except Exception as e:
        print(f"Error inserting item: {e}")
        return False
    
def get_template(novel_name: str, table, template_type: str) -> dict:
    try:
        response = table.get_item(
            Key={"novel_name": novel_name, 
                    "template_type": template_type}
        )
        # print(f"Successfully retrieved template: {response}")
        return response.get("Item")
    except Exception as e:
        print(f"Error fetching item: {e}")
        return None
        
    
test_pair = TextCompletionPromptTemplate(
    novel_name="first novel",
    template_type="novel_completion", 
    prompt_template="You are a creative and talented novel writer's assistant. Your task is to continue writing the story based on the provided context.\nUse the \"Relevant Information\" from the user's World Bible to ensure consistency with characters, plot points, and settings.\n\nRelevant Information from the World Bible:\n{context}\n\nSummary of the story so far:\n{chat_history}\n\nThe most recent part of the story:\n{input}\n\nContinue the story from here, weaving in the relevant information naturally:", 
    date=datetime.today(), 
    version=0.1
    )

# res = insert_kv_pair(item = test_pair, 
#                      table=prompt_templates_table)

# res = get_template(novel_name="first novel",
#                    template_type="novel_completion",
#                    table=prompt_templates_table)
# print(res.get("prompt_template"))

s3_client = boto3.client("s3")

bucket_name = "novelwriter-stories-primary-26-11-2025"

def upload_novel_text(text: str, filepath: str, bucket_name: str) -> bool:
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filepath,
            Body=text,
            ContentType="plain/text"
        )
    except Exception as e:
        print(f"Error putting object: {e}")
        return False
    return True

# res = upload_novel_text(
#     text="""
#     Chapter 1
# 	Through the clamorous din of the battle: the feral orcs smashing their ugly swords and axes against shield and scale, delivering wound after wound to his men, crying out foul insults in their harsh tongues, Shedinn tried to focus on his prayer. A call to the Great Mother Tamara, the dragon Goddess of life, mercy, and healing, "Grant your eternal mercy to this champion of the dragonborn, restore spirit to him once again, and let him rise up faster and stronger, O Mother. He is a Daedendrainn, and the blood of the mighty Shalash, your great servant, runs strong through his veins. Give strength to my brother!" 
#     And from unconsciousness did he rise up, strong! Balasar of the Daedendrainn clan: chieftain, favoured of the Gods, and King of the Shesten highlands and Ranhas shore. His great grey muscled frame towered a head above the rest of the combatants, righteous fury blazed like hot coal in his eyes, and the runes tattooed on his scales glowed a warm yellow - the colour of vitality. "I'm in your debt, brother", he thanked his younger sibling and picked up his heavy zweihander. Balasar had named it "Javok" - the dragonborn word for friend - after a dear very friend who had gifted it to him, who had long since died to a treacherous Yuan-Ti ambush in the Aass-Nag jungle. The greatsword had runes etched on its long blade as well, but instead of arcane spells they read his friend's name: Ssarki, who now was helping Balasar from the beyond, conjuring fiery tongues from its length that lashed at and licked the air with great hunger. Runes glowing a vibrant reddish-orange, Balasar ran into the heat of the battle, thundering steps kicking off fistfuls of dust towards the sky. He slashed and pierced, dodged and parried, and cleaved his way through the orc horde; his eyes set on their savage warchief who had hacked flesh from his arms and knocked him out seconds earlier. A few dragonborn fighters had then stepped in the way, allowing for Shedinn to work his healing spell. "FACE ME, SCUM!" yelled the mighty Balasar, and forcefully shoved a smaller orc aside, pointing his flaming Javok at the enemy.
#     The wind picked up speed, invigorating Javok's fiery tendrils, as though the Gods themselves had cast their lot with the dragonborn. And why would they not? No hard lesson was worth the destruction these orcs would wreak if they won; these orcs from the barbarian Tymras lowlands, filled with all manner of uncivilized creatures whose sole purpose in life was loot and conquest. "Their Gods care only about subjugation. Mine bring life, order, and peace", thought Shedinn, whose resolve had grown unbreakable as rock, and he willed into existence a shimmering healer's staff made of spiritual energy - a boon from his Gods. He made a quick slapping motion with right hand, and his staff dissapeared; then reappeared mid-swing a few feet to the side of orcish warchief, and crashed into his skull-helmeted head. He ate the blow with a grunt, but this momentary distraction was all that Balasar needed. He charged and swung once from the right, burning through the brute's crude shoulder plate and buried Javok into his flesh. The flames leapt and enveloped the orc's left side, binding him with ropes of furious fire. The second strike came from the left immediately afterwards, this time aimed at his abdomen. The warchief deflected this blow with the head of greataxe. As orcs were wont to do, he screamed in frustration, and blood and rage filled his already-taut muscles, and strained against his crawling shackles. With a great heave, he broke through his fiery restraints, and swung his giant axe at Balasar. He missed, then the duel began. Swing by swing, cut by cut, Balasar pushed to the frontfoot, only to be taken by suprise by a powerful helmeted headbutt from the savage. Forehead split open, he reeled back from the impact, and was struck once again in his damaged left arm by swift lateral axe swing. Jets of blood mixed with the dust, and Balasar could taste iron in the air. He felt the strength leave his wounded arm, his grip loosened, and Balasar knew he must act quickly or face certain death. That would not do. Dropping his trusted friend, his Javok, he drew a curved dagger, sharp white steel on black iron, from his waistband and skillfully feigned a drop to one knee, and slashed at the orc's ankle, severing a tendon. "One", thought Balasar as his foe stumbled, and plunged the dagger upwards into his sternum, using his foe's bodyweight to drive the point of the dagger through the boiled leather armour and the ribs. "Two". He extracted his dagger in one smooth motion and felt the orc go limp, as a sudden torrent of bright red blood painted his thighs; "Got the heart...". Balasar snuffed out his foe's life with a swift cut to the jugular, and bellowed his victory for the world to hear.
#     "Praise the Gods" thought Shedinn in exultation. He took in the sight of his mighty brother:"
#     """,
#     filepath=f"abs/prologue-{datetime.today().strftime('%d-%m-%Y')}.txt",
#     bucket_name=bucket_name
# )

# print(res)

s3_client = boto3.client('s3')

def get_story_from_s3(bucket: str, object_key: str) -> str | None:
    """
    Fetches a story object from an S3 bucket and returns its content.

    :param bucket: The name of the S3 bucket.
    :param object_key: The key (path) of the object in the S3 bucket.
    :return: The content of the story as a string, or None if an error occurs.
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=object_key)
        # The object's content is in the 'Body', which is a streaming object
        story_content = response['Body'].read().decode('utf-8')
        return story_content
    except s3_client.exceptions.NoSuchKey:
        print(f"Error: The object with key '{object_key}' does not exist in bucket '{bucket}'.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

story = get_story_from_s3(bucket="novelwriter-stories-primary-26-11-2025",
                          object_key="abs/prologue-27-11-2025.txt")
if story:
    print("--- Story Content ---")
    print(story)