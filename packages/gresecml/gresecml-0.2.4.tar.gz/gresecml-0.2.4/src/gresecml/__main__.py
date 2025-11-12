import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TensorFlow logging from console
import click
from gresecml.commands.tensorflow_group import tf as tf_group
from pyfiglet import Figlet


class BannerGroup(click.Group):
    def format_help(self, ctx, formatter):
        custom_banner = Figlet(font='slant') # Create a custom banner with 'slant' font
        click.echo(click.style(custom_banner.renderText("GresecML"), fg='yellow')) # Print banner in yellow
        super().format_help(ctx, formatter) # Call the original help formatter

@click.group(cls=BannerGroup) # Use the custom BannerGroup for the main CLI group
def main():
    """GresecML - A Machine Learning Network Traffic Analysis Tool."""
    pass
main.add_command(tf_group)