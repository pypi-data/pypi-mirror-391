import pandas as pd
import click

# Convert DataFrame to HTML file with or without full output
def dataframe_to_html(df: pd.DataFrame, path: str = None, enable_full_output: bool = False, columns_to_exclude: list = None, sort_by: str = 'prediction_normal'):
    """Convert DataFrame to HTML file."""

    df = df.sort_values(by=[sort_by], ascending=True)

    # Drop unwanted columns if they exist
    unwanted_columns = ['time_mean', 'time_std', 'bytes_mean', 'bytes_std', 'inter_arrival_std', 'inter_arrival_min', 'inter_arrival_max']

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

    # Drop unwanted columns if they exist
    unwanted_columns = ['time_mean', 'time_std', 'bytes_mean', 'bytes_std', 'inter_arrival_std', 'inter_arrival_min', 'inter_arrival_max', 'flag_syn_count', 'flag_ack_count', 'flag_fin_count', 'flag_rst_count', 'flag_dns_count', 'successful_connection', 'num_of_dest_unreachable']

    if not enable_full_output:
        for col in columns_to_exclude:
            if col in df.columns:
                df = df.drop(columns=[col])

    click.echo(df.to_string(index=False))