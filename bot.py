print("DEBUG: FILE LOADING COMPLETE")

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Debug print
print("Loaded token:", TOKEN)

# ================================
# 2. Intents (what the bot can see)
# ================================
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

# ================================
# 3. Create bot
# ================================
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    description="A Discord bot inspired by algebraic topology and cohomology."
)

# ================================
# 4. Helper functions: toy algebraic topology
# ================================

def simplicial_complex_from_edges(edges):
    """
    edges: list of tuples (u, v) representing 1-simplices between vertices.
    Returns:
        vertices: sorted list of vertices
        edges_sorted: sorted list of edges (with u < v)
    """
    vertices = set()
    edges_sorted = []

    for (u, v) in edges:
        if u == v:
            continue  # ignore loops
        a, b = sorted((u, v))
        vertices.add(a)
        vertices.add(b)
        if (a, b) not in edges_sorted:
            edges_sorted.append((a, b))

    vertices = sorted(vertices)
    edges_sorted = sorted(edges_sorted)
    return vertices, edges_sorted


def betti_numbers_1d(vertices, edges):
    """
    Very simplified Betti numbers for a 1-dimensional simplicial complex
    (just vertices and edges). This is a toy model, not full generality.

    beta0 = number of connected components
    beta1 = number of independent 1-cycles (loops)

    We use:
      beta0 = number of connected components
      beta1 = E - V + beta0      (Euler characteristic relation in 1D)
    """

    # Build adjacency list for graph connectivity
    adj = {v: [] for v in vertices}
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Count connected components with DFS
    visited = set()
    def dfs(start):
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                for nei in adj[node]:
                    if nei not in visited:
                        stack.append(nei)

    components = 0
    for v in vertices:
        if v not in visited:
            components += 1
            dfs(v)

    V = len(vertices)
    E = len(edges)
    beta0 = components
    beta1 = E - V + beta0

    return beta0, beta1


def euler_characteristic(beta0, beta1):
    """
    For a 1D complex, chi = beta0 - beta1.
    """
    return beta0 - beta1


# ================================
# 5. Events
# ================================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

    # Set bot to appear online
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("Cohomology Magic ✨")
    )

# ================================
# 6. Commands
# ================================

@bot.command(name="hello")
async def hello(ctx):
    """
    Simple ping-style command.
    """
    await ctx.send(f"Hi {ctx.author.mention}! I'm your algebraic topology bot 🌀")


@bot.command(name="simplicial")
async def simplicial(ctx, *, edge_str: str):
    """
    Parse a simple edge list and compute toy Betti numbers & Euler characteristic.

    Usage example:
        !simplicial a-b, b-c, c-a

    or
        !simplicial v1-v2, v2-v3, v3-v1, v3-v4
    """
    # Parse edge string like "a-b, b-c, c-a"
    parts = edge_str.split(",")
    edges = []

    for part in parts:
        part = part.strip()
        if "-" not in part:
            continue
        u, v = part.split("-")
        u = u.strip()
        v = v.strip()
        if u and v:
            edges.append((u, v))

    if not edges:
        await ctx.send("I couldn't parse any edges. Use format like: `a-b, b-c, c-a`.")
        return

    vertices, edges_sorted = simplicial_complex_from_edges(edges)
    beta0, beta1 = betti_numbers_1d(vertices, edges_sorted)
    chi = euler_characteristic(beta0, beta1)

    # build a nice message
    edges_text = ", ".join([f"{u}-{v}" for (u, v) in edges_sorted])
    vertices_text = ", ".join(vertices)

    msg = (
        "**Simplicial complex summary**\n"
        f"• Vertices: {vertices_text}\n"
        f"• Edges: {edges_text}\n"
        f"• β₀ (components): {beta0}\n"
        f"• β₁ (1-dimensional holes): {beta1}\n"
        f"• Euler characteristic χ = β₀ − β₁ = {chi}\n\n"
        "_Note: this is a simplified 1D example, like a graph viewed as a simplicial complex._"
    )

    await ctx.send(msg)


@bot.command(name="cohomology_vibes")
async def cohomology_vibes(ctx):
    """
    Sends a random 'cohomology mood' message.
    """
    vibes = [
        "Today your cochains are all closed **and** exact. Pure harmony. ✨",
        "Your life has nontrivial cohomology in degree 1: loops of thought that never quite vanish. 🔁",
        "Yesterday's problems? They differ by a coboundary. Same class, new representative. ♻️",
        "Your room has β₀ = 1 (connected) but an infinite-dimensional H¹ of unfinished projects. 📚",
        "Sometimes, the best you can do is pass to cohomology and ignore exact noise. 🧘‍♀️",
    ]
    import random
    await ctx.send(random.choice(vibes))


# ================================
# 7. Run the bot
# ================================
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN not found. Did you create a .env file?")
    bot.run(TOKEN)
