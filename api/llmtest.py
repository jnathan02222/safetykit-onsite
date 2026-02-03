from transformers import AutoModelForCausalLM, AutoTokenizer
from db import DB
import asyncio
from integrations.types import Relation, Edge, Artist
from bs4 import BeautifulSoup
from tqdm import tqdm


async def main():
    db = DB()

    model_name = "Qwen/Qwen2.5-0.5B-Instruct"

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    edges = [
        Edge(
            source=Artist(id=0, name="Radiohead"),
            target=Artist(id=1, name="David Byrne"),
            wikipedia_description="""Kid A is credited for pioneering the use of the internet to stream and promote music.[349][350] The pay-what-you-want release for In Rainbows is credited as a major step for music distribution.[351][114][112] Forbes wrote that it "helped forge the template for unconventional album releases in the internet age", ahead of artists such as Beyoncé and Drake.[350] Speaking at Radiohead's induction into the Rock and Roll Hall of Fame in 2019, the Talking Heads singer David Byrne, an early influence on Radiohead, praised their musical and release innovations, which he said had influenced the entire music industry.[227]""",
        ),
        Edge(
            source=Artist(id=0, name="Radiohead"),
            target=Artist(id=1, name="Talking Heads"),
            wikipedia_description="""In late 1991, Colin happened to meet the EMI A&R representative Keith Wozencroft at a record shop and handed him a copy of the demo.[17] Wozencroft was impressed and attended a performance.[17] That November, On a Friday performed at the Jericho Tavern to an audience that included several A&R representatives. It was only their eighth gig, but they had attracted interest from several record companies.[17] A Melody Maker review praised their promise and "astonishing intensity", but said their name was "terrible".[19] On 21 December, On a Friday signed a six-album recording contract with EMI.[6][17] At EMI's request, they changed their name; "Radiohead" was taken from the song "Radio Head" on the Talking Heads album True Stories (1986).[6] Yorke said the name "sums up all these things about receiving stuff ... It's about the way you take information in, the way you respond to the environment you're put in."[17]""",
        ),
    ]
    async for edge in db.all_edges(Relation.WIKIPEDIA):
        if not edge.source.name == "Staffan Österlind":
            continue
        edges.append(edge)
        if len(edges) == 3:
            break

    for edge in tqdm(edges):
        if not edge.wikipedia_description:
            continue

        # Something I hate about LLMs is how finicky they are
        # Seems to do pretty poorly with a 1 stage multiple choice prompt
        # Will also sometimes randomly fail

        # Example:
        # Yes, the paragraph explicitly states that Staffan Österlind is inspired or influenced by ABBA.
        # The relevant sentence is: "Österlind plays with ARRIVAL From Sweden-The Music of ABBA [26] (original
        # ABBA bassist Mike Watson)"

        # Heuristic: don't check for vice versa
        # Articles don't usually mention bands they inspired, but who they were inspired by

        # Notes: a false negative is probably better than a false positive

        # Need to speed up 25x so it doesn't take 2 days

        # So in summary accuracy and speed are both issues

        prompt = f"""
        Consider the following paragraph from the Wikipedia article on {edge.source.name}:

        {BeautifulSoup(edge.wikipedia_description, "html.parser").get_text()}

        Does the paragraph EXPLICITLY say {edge.source.name} was inspired or influenced by {edge.target.name}.

        """
        messages = [
            {
                "role": "system",
                "content": "You are an LLM responsible for annotating paragraphs on musician relationships",
            },
            {"role": "user", "content": prompt},
        ]

        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(**model_inputs, max_new_tokens=512)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        print(response)


asyncio.run(main())
