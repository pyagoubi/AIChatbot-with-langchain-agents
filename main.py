import json
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk, PhotoImage
from agent import create_agent, query_agent
from no_agent import easy_mode
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    return json.loads(response)


class SetupApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Chatbot Setup")
        self.geometry("400x200")

        self.api_key = tk.StringVar()

        self.label = ttk.Label(self, text="Enter your OpenAI API Key:")
        self.label.pack(pady=20)

        self.api_entry = ttk.Entry(self, textvariable=self.api_key, width=40)
        self.api_entry.pack(pady=10)

        self.submit_button = ttk.Button(self, text="Submit", command=self.start_chat_application)
        self.submit_button.pack(pady=10)

    def start_chat_application(self):
        api_key = self.api_key.get()
        self.destroy()
        chat_application = ChatApplication(api_key)
        chat_application.mainloop()




class ChatApplication(tk.Tk):
    def __init__(self, api_key):
        super().__init__()

        self.title("AI Chatbot")
        self.geometry("400x600")

        self.api_key = api_key

        self.conversation = []

        # Create an invisible icon and use it
        self.invisible_icon = PhotoImage(width=1, height=1)
        self.iconphoto(True, self.invisible_icon)

        # Define the styles for the widgets
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), background='grey', foreground='black')
        style.configure('TEntry', font=('Arial', 10))

        self.configure(bg='black')

        # Configure chat_display
        self.chat_display = tk.Text(self, wrap="word", font=("Arial", 12), bg='white', fg='black')
        self.chat_display.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Define a single frame to hold both chat_entry and send_button
        self.entry_button_frame = tk.Frame(self, bg='black')
        self.entry_button_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.chat_entry = ttk.Entry(self.entry_button_frame, style='TEntry', width=50)
        self.chat_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.send_button = ttk.Button(self.entry_button_frame, text="Send", command=self.send_message, style='TButton')
        self.send_button.grid(row=0, column=1, padx=(0, 20))

        # Create tags for the chat display Text widget with various font colors
        self.chat_display.tag_configure("user", foreground="blue")
        self.chat_display.tag_configure("chatbot", foreground="black")


        # Configure the grid weights to allow resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.entry_button_frame.columnconfigure(0, weight=1)

        self.bind('<Return>', self.send_message)

    def write_response(self, decoded_response, message):
        if "bar" in decoded_response:
            self.show_bar_chart(decoded_response)
        elif "line" in decoded_response:
            self.show_line_chart(decoded_response)
        elif "table" in decoded_response:
            self.show_table(decoded_response)
        else:
            self.update_chat_display(message, decoded_response["answer"])

    def send_message(self, event=None):
        message = self.chat_entry.get()

        # Clear the entry box
        self.chat_entry.delete(0, tk.END)

        self.conversation.append({"role": "system", "content": "User input: " + message})

        try:
            agent = create_agent(API_KEY=self.api_key, pandas_agent=True)
            response = query_agent(agent=agent, query=message)
            decoded_response = decode_response(response)
            self.write_response(decoded_response, message)
        except:
            try:
                agent = create_agent(API_KEY=self.api_key, pandas_agent=False)
                response = query_agent(agent=agent, query=message)
                decoded_response = decode_response(response)
                self.write_response(decoded_response, message)
            except:
                try:
                    response = easy_mode(input_text=self.user_input, openaikey=self.user_api_key)
                    self.update_chat_display(message, response)
                except:
                    self.update_chat_display(message, "Sorry, I can not answer that question")



    def show_bar_chart(self, data):
        # Create a new window for the chart
        chart_window = tk.Toplevel(self)
        #chart_window.title("Bar Chart")

        # Extract the column labels and data from the provided format
        columns = data["bar"]["columns"]
        data_values = data["bar"]["data"]

        # Create a figure and axis for the bar chart
        fig, ax = plt.subplots()

        # Plot the bar chart
        ax.bar(columns, data_values)

        # Set labels and title
        ax.set_xlabel("Columns")
        ax.set_ylabel("Data Values")
        ax.set_title("Bar Chart")

        # Create a canvas to display the figure
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()

        # Pack the canvas into the chart window
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def show_line_chart(self, data):
        # Create a new window for the line chart
        chart_window = tk.Toplevel(self)
        #chart_window.title("Line Chart")

        # Extract the column labels and data from the provided format
        columns = data["line"]["columns"]
        data_values = data["line"]["data"]

        # Create a figure and axis for the line chart
        fig, ax = plt.subplots()

        # Plot the line chart
        ax.plot(columns, data_values)

        # Set labels and title
        ax.set_xlabel("Columns")
        ax.set_ylabel("Data Values")
        ax.set_title("Line Chart")

        # Create a canvas to display the figure
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()

        # Pack the canvas into the chart window
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def show_table(self, data):
        # Create a new window for the table
        table_window = tk.Toplevel(self)
        table_window.title("Table")

        # Extract the column labels and data from the provided format
        columns = data["table"]["columns"]
        data_values = data["table"]["data"]

        # Create a table using ttk.Treeview
        table = ttk.Treeview(table_window, columns=columns, show="headings")

        # Set column headings
        for col in columns:
            table.heading(col, text=col)

        # Add data rows to the table
        for row in data_values:
            table.insert("", tk.END, values=row)

        # Pack the table into the table window
        table.pack(fill=tk.BOTH, expand=True)

    def update_chat_display(self, user_message, bot_message):
        # insert "User: " label with color blue
        self.chat_display.insert(tk.END, "\n\nUser: ", "user")

        # insert user message in regular color (default black)
        self.chat_display.insert(tk.END, user_message)

        # insert "AI-Chatbot: " label with color black
        self.chat_display.insert(tk.END, "\n\nAI-Chatbot: ", "chatbot")

        self.chat_display.insert(tk.END, bot_message)

        # Auto scroll to the end
        self.chat_display.see(tk.END)


if __name__ == "__main__":
    setup_application = SetupApplication()
    setup_application.geometry("400x200")
    setup_application.mainloop()
