import pandas as pd
import click

def output_dataframe(df: pd.DataFrame, path: str = None, enable_full_output: bool = False, columns_to_exclude: list = None, sort_by: str = 'prediction_normal', verbose = False):
    """Output DataFrame to file and/or print to console."""

    # Print to console if verbose is enabled
    if verbose: 
        print_dataframe(df, enable_full_output, columns_to_exclude, sort_by)
    
    # Get extension of output file
    out_extension = None
    if path is not None:
        try:
            out_extension = path.split('.')[-1].lower()
        except:
            out_extension = None
            raise ValueError("Could not determine output file extension.")
        
    match out_extension:
        case 'html':
            dataframe_to_html(df, path, enable_full_output, columns_to_exclude, sort_by)
        case _: 
            raise ValueError("Unsupported output file format. Currently only HTML is supported.")

# Convert DataFrame to HTML file with or without full output
def dataframe_to_html(df: pd.DataFrame, path: str = None, enable_full_output: bool = False, columns_to_exclude: list = None, sort_by: str = 'prediction_normal'):
    """Convert DataFrame to HTML file."""

    df = df.sort_values(by=[sort_by], ascending=True)

    if not enable_full_output:
        for col in columns_to_exclude:
            if col in df.columns:
                df = df.drop(columns=[col])

    if path is not None:
        try:
            df.to_html(path, index=False)
            click.echo(click.style(f"Saved output to: {path}", fg='yellow'))
        except Exception as e:
            click.echo(click.style(f"Error saving output to: {path}\n{str(e)}", fg='red'))
            return


# Print DataFrame to console with or without full output
def print_dataframe(df: pd.DataFrame, enable_full_output: bool = False, columns_to_exclude: list = None, sort_by: str = 'prediction_normal'):
    """Print DataFrame to console."""

    df = df.sort_values(by=[sort_by], ascending=True)

    if not enable_full_output:
        for col in columns_to_exclude:
            if col in df.columns:
                df = df.drop(columns=[col])

    click.echo(df.to_string(index=False))