import click
import os
import pathlib
import collections

from .parse import Chat, Message


@click.group()
@click.version_option(package_name="telegramstats", prog_name="telegramstats")
@click.pass_context
def telegramstats(ctx: click.Context):
    """
    Get interesting stats from Telegram chat exports.
    """

    ctx.max_content_width = 10000
    ctx.show_default = True

@telegramstats.group()
def single():
    """
    Process single-chat Telegram GDPR exports.
    """
    pass

@single.command()
@click.argument(
    "export_path",
    nargs=-1,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        allow_dash=True,
        path_type=pathlib.Path,
    ),
)
def counts_by_user(
    export_path: list[pathlib.Path],
):
    """
    Get cumulative message counts for each user in the given chats.
    """

    chats = []
    with click.progressbar(export_path, label="Parsing JSON") as paths:
        for path in paths:
            if path.is_dir():
                path = path / "result.json"
            chat = Chat.from_singlechat_export(path)
            chats.append(chat)

    counts = collections.defaultdict(lambda: 0)
    ids = collections.defaultdict(set)

    for chat in chats:
        with click.progressbar(chat.messages, label=chat.name) as messages:
            for message in messages:
                if not message.from_id:
                    continue
                counts[message.from_id] += 1
                ids[message.from_id].add(message.from_)

    for actor_id, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        valid_aliases = []
        for alias in ids[actor_id]:
            if alias is None:
                continue
            valid_aliases.append(alias)
        
        if len(valid_aliases) == 0:
            displayed_aliases = f"Deleted account ({actor_id})"
        else:
            displayed_aliases = " / ".join(valid_aliases)

        click.echo(
            click.style(f"{count}", bold=True) +
            "\t" +
            click.style(displayed_aliases, italic=True),
        )


if __name__ == "__main__":
    telegramstats()
