# Cog used by https://github.com/pvyParts/allianceauth-discordbot

# Cog Stuff
from discord import AutocompleteContext, Interaction, Option, SlashCommandGroup
from discord.ext import commands
from discord.embeds import Embed

# AA Contexts
from aadiscordbot.cogs.utils.decorators import sender_has_perm
from aadiscordbot.app_settings import get_all_servers, get_site_url
from django.core.exceptions import ObjectDoesNotExist
from eveuniverse.models.universe_1 import EveType

from fittings.models import Fitting, Doctrine, Category
from fittings import __version__
from django.db.models import Q

import logging
logger = logging.getLogger('aadiscordbot.cogs.fittings')


class Fittings(commands.Cog):
    """
    A Cog to query the details of Fittings, Doctrines and Categories
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    fittings_commands = SlashCommandGroup(
        "fittings", 
        "Fittings",
        guild_ids=get_all_servers())

    async def search_fittings(self, ctx: AutocompleteContext) -> list[str]:
        return list(Fitting.objects.filter(Q(name__icontains=ctx.value) | Q(ship_type__name__icontains=ctx.value)).values_list('name', flat=True)[:10])

    async def search_shiptype(self, ctx: AutocompleteContext) -> list[str]:
        return list(EveType.objects.filter(name__icontains=ctx.value, eve_group__eve_category=6, published=True).values_list('name', flat=True)[:10])

    async def search_doctrine(self, ctx: AutocompleteContext) -> list[str]:
        return list(Doctrine.objects.filter(name__icontains=ctx.value).values_list('name', flat=True)[:10])
    
    async def search_category(self, ctx: AutocompleteContext) -> list[str]:
        return list(Category.objects.filter(name__icontains=ctx.value).values_list('name', flat=True)[:10])
    
    @fittings_commands.command(name="about")
    async def about(self, ctx) -> Interaction:
        """
        About the Fittings App providing this Cog
        """
        embed = Embed(title="Fittings")
        embed.description = "https://gitlab.com/colcrunch/fittings"
        embed.url = "https://gitlab.com/colcrunch/fittings"
        embed.set_thumbnail(url="https://gitlab.com/uploads/-/system/project/avatar/15275953/icons8-work-128.png")
        embed.set_footer(text="Developed Col Crunch")
        embed.add_field(name="Version", value=f"{__version__}", inline=False)

        return await ctx.respond(embed=embed)

    @fittings_commands.command(name="fit")
    @sender_has_perm('fittings.access_fittings')
    async def fit(self, ctx, search_fittings=Option(str, "Fitting", autocomplete=search_fittings)) -> Interaction:
        """
        Returns fits matching the exact name given
        """
        await ctx.trigger_typing()
        await ctx.respond(content=f"Searching for {search_fittings}", ephemeral=True)

        try:
            fits = Fitting.objects.filter(name=search_fittings)
            for fit in fits:
                embed = fitting_details(fit)
                await ctx.respond(embed=embed, allowed_mentions=None)
        except ObjectDoesNotExist:
            return await ctx.respond("No Fits Found", allowed_mentions=None, ephemeral=True)

    @fittings_commands.command(name="fit_ship")
    @sender_has_perm('fittings.access_fittings')
    async def fit_shiptype(self, ctx, search_shiptype=Option(str, "Ship Type", autocomplete=search_shiptype)) -> Interaction:
        """
        Returns fittings for a Ship Type
        """
        await ctx.trigger_typing()
        await ctx.respond(content=f"Searching for {search_shiptype}", ephemeral=True)

        try:
            fits = Fitting.objects.filter(ship_type__name=search_shiptype)
            for fit in fits:
                embed = fitting_details(fit)
                await ctx.respond(embed=embed, allowed_mentions=None)
        except ObjectDoesNotExist:
            return await ctx.respond("No Fits Found for this Ship Type", allowed_mentions=None, ephemeral=True)

    @fittings_commands.command(name="doctrine")
    @sender_has_perm('fittings.access_fittings')
    async def doctrine(self, ctx, search_doctrine=Option(str, "Doctrine", autocomplete=search_doctrine)) -> Interaction:
        """
        Return information on a Fitting Doctrine
        """
        await ctx.trigger_typing()
        await ctx.respond(content=f"Searching for {search_doctrine}", ephemeral=True)
        
        try:
            doctrines = Doctrine.objects.filter(name__icontains=search_doctrine)
            for doctrine in doctrines:
                embed = doctrine_details(doctrine)
                await ctx.respond(embed=embed, allowed_mentions=None)
        except ObjectDoesNotExist:
            return await ctx.respond("No Doctrine Found", allowed_mentions=None, ephemeral=True)

    @fittings_commands.command(name="category")
    @sender_has_perm('fittings.access_fittings')
    async def category(self, ctx, search_category=Option(str, "Category", autocomplete=search_category)) -> Interaction:
        """
        Return information on a Fitting Category
        """
        await ctx.trigger_typing()
        await ctx.respond(content=f"Searching for {search_category}", ephemeral=True)
        
        try:
            categories = Category.objects.filter(name__icontains=search_category)
            for category in categories:
                embed = category_details(category)
                await ctx.respond(embed=embed, allowed_mentions=None)
        except ObjectDoesNotExist:
            return await ctx.respond("No Categories Found", allowed_mentions=None, ephemeral=True)


def fitting_details(fit: Fitting) -> Embed:
    """Returns a nice formatted Embed with details on a given fit

    Args:
        fit (Fitting): fittings.model.fitting

    Returns:
        Embed: discord.embed
    """    
    
    embed = Embed(title=f"{fit.ship_type.name}: {fit.name}")
    embed.set_thumbnail(
        url=f"https://images.evetech.net/types/{fit.ship_type_type_id}/render?size=128"
    )
    embed.description = fit.description

    doctrines_value = ''
    for doctrine in Doctrine.objects.filter(fittings=fit).values("name", "id"):
        doctrines_value += f"{doctrines_value}[{doctrine['name']}]({get_site_url()}/fittings/doctrine/{doctrine['id']}/)\n"
    if doctrines_value == '':
        doctrines_value = 'None'

    category_value = ''
    for category in Category.objects.filter(fittings=fit).values("name", "id"):
        category_value += f"{category_value}[{category['name']}]({get_site_url()}/fittings/cat/{category['id']}/)\n"
    if category_value == '':
        category_value = 'None'

    embed.add_field(
        name="Doctrines:",
        value=doctrines_value
    )
    embed.add_field(
        name="Categories",
        value=category_value
    )
    embed.add_field(
        name="URL",
        value=f"{get_site_url()}/fittings/fit/{fit.id}/",
        inline=False
    )
    return embed


def doctrine_details(doctrine: Doctrine) -> Embed:
    """Returns a nice formatted Embed with details on a given doctrine

    Args:
        doctrine (Doctrine): fittings.model.doctrine

    Returns:
        Embed: discord.embed
    """
    embed = Embed(title=doctrine.name)
    embed.set_thumbnail(
        url=doctrine.icon_url
    )
    embed.description = doctrine.description

    for fit in doctrine.fittings.all():
        embed.add_field(
            name=fit.ship_type.name,
            value=f"[{fit.name}]({get_site_url()}/fittings/fit/{fit.id}/)"
        )

    embed.add_field(
        name="URL",
        value=f"{get_site_url()}/fittings/doctrine/{doctrine.id}/",
        inline=False
    )

    return embed


def category_details(category: Category) -> Embed:
    """Returns a nice formatted Embed with details on a given category

    Args:
        category (Category): fittings.model.category

    Returns:
        Embed: discord.embed
    """
    embed = Embed(title=category.name)

    for doctrine in category.doctrines.all():
        embed.add_field(
            name=doctrine.name,
            value=f"[{doctrine.name}]({get_site_url()}/fittings/doctrine/{doctrine.id}/)"
        )
    embed.add_field(
        name="URL",
        value=f"{get_site_url()}/fittings/cat/{category.id}/",
        inline=False
    )

    return embed


def setup(bot) -> None:
    bot.add_cog(Fittings(bot))
