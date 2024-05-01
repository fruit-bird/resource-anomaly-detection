import streamlit as st
from dynamic_auto_scaling.analyze import AVAILABLE_METRICS, AVAILABLE_MODELS, analyze
import matplotlib.pyplot as plt
import mpld3
import streamlit.components.v1 as components


def main():
    st.title("Anomaly Detection")

    selected_metric = st.sidebar.selectbox("Select Metric", AVAILABLE_METRICS)
    selected_model = st.sidebar.selectbox("Select Model", AVAILABLE_MODELS)

    if st.sidebar.button("Analyze"):
        df, anomalies = analyze(selected_metric, selected_model)
        if df is not None:
            # Plot the line char
            fig = plt.figure(figsize=(10, 6))
            plt.plot(df[selected_metric], label=f"{selected_metric}")

            # Mark the anomalies with red points
            anomalies_indices = df.index[anomalies]
            plt.scatter(
                anomalies_indices,
                df.loc[anomalies_indices, selected_metric],
                color="red",
                label="Anomalies",
            )

            plt.title(f"Anomaly Detection for {selected_metric}")
            plt.xlabel("Time")
            plt.ylabel(selected_metric)
            plt.grid(True, linewidth=0.1)
            plt.legend()

            fig_html = mpld3.fig_to_html(fig)
            components.html(fig_html, width=900, height=700)

            st.write(f"Number of Anomalies Detected: {anomalies.sum()}")
            # Describe the data
            st.write("## Descriptive Statistics")
            st.dataframe(df.describe())
        else:
            st.write("Something went wrong, please try again.")


if __name__ == "__main__":
    main()
