"""
Content banks for the discipline / mental-toughness niche.

Everything here is original, royalty-free phrasing written in an intense,
no-excuses motivational voice (Goggins / Jocko energy) so you can record it,
caption it, and post it without copyright headaches.

The generator pulls from these banks and assembles fresh scripts each run.
Add your own lines to any list and the generator instantly uses them.
"""

# Each theme is a self-contained world: hooks grab the scroll, body lines
# escalate, and closers land the punch. Keep lines SHORT — they double as
# on-screen text overlays for reposting/clip-style videos.

THEMES = {
    "wake_up_early": {
        "label": "5AM / Wake Up Early",
        "hooks": [
            "While they were sleeping, you were becoming someone they can't beat.",
            "The alarm went off. You have two seconds to decide who you are.",
            "Nobody respects the version of you that hits snooze.",
            "5AM doesn't care how you feel. That's why it works.",
            "The hardest rep of your day is the one that gets you out of bed.",
        ],
        "body": [
            "The world rewards the people who show up before they're ready.",
            "Comfort is a slow death you agree to one snooze at a time.",
            "Winning the morning isn't motivation. It's a war you fight in the dark.",
            "Every second you lie there, someone hungrier is already moving.",
            "You don't rise to your goals. You fall to your habits.",
            "The bed feels good because it's quietly stealing your future.",
            "Discipline starts the moment your feet hit the floor and your mind says no.",
        ],
        "closers": [
            "Get up. Before the excuses wake up too.",
            "The morning is won in the dark. Go get it.",
            "Stop negotiating with your alarm. You already lost that fight.",
            "Beat the sun. Earn the day.",
        ],
    },
    "no_excuses": {
        "label": "No Excuses",
        "hooks": [
            "Your excuse is just a comfortable lie wearing a good outfit.",
            "Nobody is coming to save you. That's the good news.",
            "You're not tired. You're under-disciplined and over-comfortable.",
            "Stop explaining why you can't. It's louder than your effort.",
            "The story you keep telling yourself is the cage you live in.",
        ],
        "body": [
            "Excuses are the receipts for the life you didn't build.",
            "Motivation is a guest. Discipline pays the rent.",
            "You will never out-talk the work you refuse to do.",
            "Every reason you give is a door you're locking from the inside.",
            "The people you envy stopped explaining and started executing.",
            "Comfort asked you a question today. Your excuse answered it.",
            "You don't need permission. You need to stop asking for it.",
        ],
        "closers": [
            "Kill the excuse. Keep the standard.",
            "No one's watching. That's exactly why it counts.",
            "Stop talking. The work doesn't care.",
            "Excuses or results. You can't post both.",
        ],
    },
    "pain_discomfort": {
        "label": "Pain & Discomfort",
        "hooks": [
            "The thing you're avoiding is the exact thing that builds you.",
            "Comfort feels safe right up until it ruins your life.",
            "You want the result but you're allergic to the price.",
            "Pain is just weakness leaving on a schedule you set.",
            "If it doesn't cost you, it won't change you.",
        ],
        "body": [
            "Growth lives on the other side of the moment you wanted to quit.",
            "You were built to do hard things. Stop dodging them.",
            "Suffering on purpose today is how you stop suffering by accident later.",
            "The voice begging you to stop is the one you have to defeat.",
            "Discomfort is the toll. Pay it or stay where you are.",
            "Soft choices build a soft life. Hard choices build a hard man.",
            "When it burns, that's the lesson. Lean in.",
        ],
        "closers": [
            "Chase the discomfort. It knows the way out.",
            "Do the hard thing. Become the hard thing.",
            "Embrace the suck. It's training you.",
            "Hurt now or regret forever. Pick one.",
        ],
    },
    "consistency": {
        "label": "Consistency / Show Up Daily",
        "hooks": [
            "You don't need a breakthrough. You need to stop breaking your streak.",
            "Motivation got you started. Only consistency keeps you alive.",
            "The boring days are the ones that actually build you.",
            "One workout won't change you. Skipping one will.",
            "You're one disciplined month away from a different life.",
        ],
        "body": [
            "Show up on the day you feel nothing. That's the day that counts.",
            "Small reps, stacked daily, become a life nobody can ignore.",
            "Quitting is loud. Consistency is quiet and it always wins.",
            "You're not behind. You just stopped showing up.",
            "The compound interest of effort is brutal and beautiful.",
            "Average is just consistency aimed at the wrong things.",
            "Do it again today. And tomorrow. And when it stops being fun.",
        ],
        "closers": [
            "Don't break the chain. Add a link.",
            "Show up. Again. That's the whole secret.",
            "Consistency is a superpower disguised as boredom.",
            "Same time tomorrow. No matter what.",
        ],
    },
    "mental_toughness": {
        "label": "Mental Toughness",
        "hooks": [
            "Your mind quits long before your body does. Train the mind.",
            "Weakness whispers. You decide if you listen.",
            "The strongest thing you'll ever do is keep going when it's pointless.",
            "Toughness isn't loud. It's the silence after you wanted to quit.",
            "You're not soft. You just never trained the part that hurts.",
        ],
        "body": [
            "Control the mind or it controls you. There's no third option.",
            "When the voice says stop, that's where the work begins.",
            "Mental toughness is doing it ugly, scared, and tired anyway.",
            "You build a callus on your mind one hard day at a time.",
            "Discipline is just remembering what you actually want.",
            "The battle was never with them. It's always been with you.",
            "Win the argument inside your head. The rest follows.",
        ],
        "closers": [
            "Stay hard. Stay moving.",
            "Master your mind or serve it. Choose.",
            "The mind breaks first. Don't let it.",
            "Outlast the voice. That's the whole game.",
        ],
    },
    "comparison_comfort": {
        "label": "Stop Comparing / Comfort Trap",
        "hooks": [
            "You're not falling behind. You're watching instead of working.",
            "Comfort is the most expensive thing you'll ever buy.",
            "Scrolling on other people's wins is how you lose your own.",
            "The trap isn't failure. It's a life that's just comfortable enough.",
            "You traded your potential for a feeling that lasts 4 seconds.",
        ],
        "body": [
            "Stop measuring your day one against their year ten.",
            "Comfort doesn't kill you. It just convinces you not to try.",
            "Every hour you compare is an hour you didn't compete.",
            "The only person worth beating is who you were yesterday.",
            "Your competition isn't online. It's the version of you that quit.",
            "Comfortable people give the best advice and live the smallest lives.",
            "Close the app. Open the chapter. Write your own.",
        ],
        "closers": [
            "Compete with yesterday. Ignore everyone else.",
            "Get uncomfortable on purpose. Today.",
            "Stop watching. Start becoming.",
            "Comfort or growth. Never both.",
        ],
    },
}

# Reusable calls-to-action that work across every theme. The generator
# rotates these so your videos drive follows/engagement (which is what the
# payout algorithms reward).
CTA_LINES = [
    "Follow for your daily reset.",
    "Save this and read it tomorrow at 5AM.",
    "Send this to someone who's about to quit.",
    "Follow if you needed to hear this today.",
    "Tag the person who needs to lock in.",
    "Comment 'LOCKED IN' if you're done making excuses.",
    "Follow for one hard truth a day.",
    "Share this with your gym partner. Hold each other accountable.",
]

# Caption openers — the first line of your post text. Short, punchy,
# stops the scroll in the feed preview.
CAPTION_HOOKS = [
    "Read this twice. 👇",
    "Nobody's coming. 🔒",
    "Save this one.",
    "If this hit, you needed it.",
    "Hard truth incoming.",
    "Day 1 or one day. You decide.",
    "Stop scrolling. Start moving.",
    "This is your sign.",
]

# Hashtag pools. The generator mixes a few "big reach" tags with a few
# "niche" tags — that combo helps discovery without getting buried.
HASHTAGS_BROAD = [
    "#motivation", "#mindset", "#discipline", "#selfimprovement",
    "#mentaltoughness", "#grind", "#noexcuses", "#hardwork",
    "#successmindset", "#growthmindset",
]
HASHTAGS_NICHE = [
    "#disciplineovermotivation", "#5amclub", "#stayhard", "#lockedin",
    "#mentalstrength", "#dailymotivation", "#selfdiscipline", "#mindsetshift",
    "#becomethatguy", "#noexcusesjustresults",
]

# Suggested production notes attached to each script so reposting/filming
# is brainless. Pair the right visual + sound and retention goes up.
VISUAL_SUGGESTIONS = [
    "B-roll: empty gym at dawn, slow push-in.",
    "B-roll: lacing up shoes in the dark, single light.",
    "Talking head, dim room, hard front light, no smile.",
    "B-roll: running on an empty road, low sun behind.",
    "Text-only on black, white bold font, line appears per beat.",
    "B-roll: cold shower / splashing water, slow-mo.",
    "B-roll: writing in a journal at a desk, overhead shot.",
    "B-roll: heavy barbell, chalk, deep breath before the lift.",
]
AUDIO_SUGGESTIONS = [
    "Slow building cinematic drums, drop on the closer.",
    "Dark piano loop, low and tense.",
    "Trending 'aggressive lo-fi' beat (check your sounds tab).",
    "Distant ambient + heartbeat thump under the voiceover.",
    "Hard-hitting orchestral swell timed to the last line.",
    "Minimal beat — let the words breathe, punch in on the close.",
]
