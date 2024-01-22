import os.path
from libs.helper import *
import streamlit as st
import uuid
import pandas as pd
import openai
from requests.models import ChunkedEncodingError
from streamlit.components import v1
from voice_toolkit import voice_toolkit

if "apibase" in st.secrets:
    openai.api_base = st.secrets["apibase"]
else:
    openai.api_base = "https://api.openai.com/v1"

st.set_page_config(
    page_title="ChatGPT Assistant", layout="wide", page_icon="🤖"
)

# Custom styling
st.markdown(css_code, unsafe_allow_html=True)

if "initial_settings" not in st.session_state:
    st.session_state["path"] = "history_chats_file"
    st.session_state["history_chats"] = get_history_chats(st.session_state["path"])
    st.session_state["delete_dict"] = {}
    st.session_state["delete_count"] = 0
    st.session_state["voice_flag"] = ""
    st.session_state["user_voice_value"] = ""
    st.session_state["error_info"] = ""
    st.session_state["current_chat_index"] = 0
    st.session_state["user_input_content"] = ""

    if os.path.exists("./set.json"):
        with open("./set.json", "r", encoding="utf-8") as f:
            data_set = json.load(f)
        for key, value in data_set.items():
            st.session_state[key] = value

    st.session_state["initial_settings"] = True

with st.sidebar:
    st.markdown("# 🤖 Chat Window")
    chat_container = st.container()
    with chat_container:
        current_chat = st.radio(
            label="Chat History Window",
            format_func=lambda x: x.split("_")[0] if "_" in x else x,
            options=st.session_state["history_chats"],
            label_visibility="collapsed",
            index=st.session_state["current_chat_index"],
            key="current_chat"
            + st.session_state["history_chats"][
                st.session_state["current_chat_index"]
            ],
        )
    st.write("---")

def write_data(new_chat_name=current_chat):
    if "apikey" in st.secrets:
        st.session_state["paras"] = {
            "temperature": st.session_state["temperature" + current_chat],
            "top_p": st.session_state["top_p" + current_chat],
            "presence_penalty": st.session_state["presence_penalty" + current_chat],
            "frequency_penalty": st.session_state["frequency_penalty" + current_chat],
        }
        st.session_state["contexts"] = {
            "context_select": st.session_state["context_select" + current_chat],
            "context_input": st.session_state["context_input" + current_chat],
            "context_level": st.session_state["context_level" + current_chat],
        }
        save_data(
            st.session_state["path"],
            new_chat_name,
            st.session_state["history" + current_chat],
            st.session_state["paras"],
            st.session_state["contexts"],
        )
def reset_chat_name_fun(chat_name):
    chat_name = chat_name + "_" + str(uuid.uuid4())
    new_name = filename_correction(chat_name)
    current_chat_index = st.session_state["history_chats"].index(current_chat)
    st.session_state["history_chats"][current_chat_index] = new_name
    st.session_state["current_chat_index"] = current_chat_index
    write_data(new_name)
    st.session_state["history" + new_name] = st.session_state["history" + current_chat]
    for item in [
        "context_select",
        "context_input",
        "context_level",
        *initial_content_all["paras"],
    ]:
        st.session_state[item + new_name + "value"] = st.session_state[
            item + current_chat + "value"
        ]
    remove_data(st.session_state["path"], current_chat)

def create_chat_fun():
    st.session_state["history_chats"] = [
        "New Chat_" + str(uuid.uuid4())
    ] + st.session_state["history_chats"]
    st.session_state["current_chat_index"] = 0

def delete_chat_fun():
    if len(st.session_state["history_chats"]) == 1:
        chat_init = "New Chat_" + str(uuid.uuid4())
        st.session_state["history_chats"].append(chat_init)
    pre_chat_index = st.session_state["history_chats"].index(current_chat)
    if pre_chat_index > 0:
        st.session_state["current_chat_index"] = (
            st.session_state["history_chats"].index(current_chat) - 1
        )
    else:
        st.session_state["current_chat_index"] = 0
    st.session_state["history_chats"].remove(current_chat)
    remove_data(st.session_state["path"], current_chat)

with st.sidebar:
    c1, c2 = st.columns(2)
    create_chat_button = c1.button(
        "New", use_container_width=True, key="create_chat_button"
    )
    if create_chat_button:
        create_chat_fun()
        st.experimental_rerun()

    delete_chat_button = c2.button(
        "Delete", use_container_width=True, key="delete_chat_button"
    )
    if delete_chat_button:
        delete_chat_fun()
        st.experimental_rerun()

with st.sidebar:
    if ("set_chat_name" in st.session_state) and st.session_state[
        "set_chat_name"
    ] != "":
        reset_chat_name_fun(st.session_state["set_chat_name"])
        st.session_state["set_chat_name"] = ""
        st.experimental_rerun()

    st.write("\n")
    st.write("\n")
    st.text_input("Set Window Name:", key="set_chat_name", placeholder="Click to input")
    st.selectbox(
        "Select Model:",
        index=0,
        options=["gpt-3.5-turbo", "gpt-4"],
        key="select_model"
    )
    st.write("\n")
    st.caption(
        """
    - Double-click on the page to locate the input bar directly.
    - Ctrl + Enter can quickly submit the question.
    """
    )
    st.markdown(
        '<a href="https://github.com/PierXuY/ChatGPT-Assistant" target="_blank" rel="ChatGPT-Assistant">'
        '<img src="https://badgen.net/badge/icon/GitHub?icon=github&amp;label=ChatGPT Assistant" alt="GitHub">'
        "</a>",
        unsafe_allow_html=True,
    )

if "history" + current_chat not in st.session_state:
    for key, value in load_data(st.session_state["path"], current_chat).items():
        if key == "history":
            st.session_state[key + current_chat] = value
        else:
            for k, v in value.items():
                st.session_state[k + current_chat + "value"] = v

container_show_messages = st.container()
container_show_messages.write("")

with container_show_messages:
    if st.session_state["history" + current_chat]:
        show_messages(current_chat, st.session_state["history" + current_chat])

if any(st.session_state["delete_dict"].values()):
    for key, value in st.session_state["delete_dict"].items():
        try:
            deleteCount = value.get("deleteCount")
        except AttributeError:
            deleteCount = None
        if deleteCount == st.session_state["delete_count"]:
            delete_keys = key
            st.session_state["delete_count"] = deleteCount + 1
            delete_current_chat, idr = delete_keys.split(">")
            df_history_tem = pd.DataFrame(
                st.session_state["history" + delete_current_chat]
            )
            df_history_tem.drop(
                index=df_history_tem.query("role=='user'").iloc[[int(idr)], :].index,
                inplace=True,
            )
            df_history_tem.drop(
                index=df_history_tem.query("role=='assistant'")
                .iloc[[int(idr)], :]
                .index,
                inplace=True,
            )
            st.session_state["history" + delete_current_chat] = df_history_tem.to_dict(
                "records"
            )
            write_data()
            st.experimental_rerun()

def callback_fun(arg):
    if (
        "history" + current_chat in st.session_state
        and "frequency_penalty" + current_chat in st.session_state
    ):
        write_data()
        st.session_state[arg + current_chat + "value"] = st.session_state[
            arg + current_chat
        ]

def clear_button_callback():
    st.session_state["history" + current_chat] = []
    write_data()

def delete_all_chat_button_callback():
    if "apikey" in st.secrets:
        folder_path = st.session_state["path"]
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith(".json") and os.path.isfile(file_path):
                os.remove(file_path)
    st.session_state["current_chat_index"] = 0
    st.session_state["history_chats"] = ["New Chat_" + str(uuid.uuid4())]

def save_set(arg):
    st.session_state[arg + "_value"] = st.session_state[arg]
    if "apikey" in st.secrets:
        with open("./set.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "open_text_toolkit_value": st.session_state["open_text_toolkit"],
                    "open_voice_toolkit_value": st.session_state["open_voice_toolkit"],
                },
                f,
            )

tap_input, tap_context, tap_model, tab_func = st.tabs(
    ["💬 Chat", "🗒️ Preset", "⚙️ Model", "🛠️ Function"]
)

with tap_context:
    set_context_list = list(set_context_all.keys())
    context_select_index = set_context_list.index(
        st.session_state["context_select" + current_chat + "value"]
    )
    st.selectbox(
        label="Select Context",
        options=set_context_list,
        key="context_select" + current_chat,
        index=context_select_index,
        on_change=callback_fun,
        args=("context_select",),
    )
    st.caption(
        """
    Select the template context. If the content of the template cannot meet your needs,
    you can manually input it in the next column.
    """
    )
    st.selectbox(
        label="Select Input",
        options=["Input", "File"],
        key="context_input" + current_chat,
        index=int(
            st.session_state["context_input" + current_chat + "value"] == "File"
        ),
        on_change=callback_fun,
        args=("context_input",),
    )
    st.caption(
        """
    You can choose to input text manually or input from a file.
    If you choose to input from a file, a file path input box will appear.
    """
    )
    if (
        st.session_state["context_input" + current_chat + "value"] == "File"
        and "context_level" + current_chat not in st.session_state
    ):
        st.session_state["context_level" + current_chat] = 1

    st.slider(
        label="Context Level",
        min_value=1,
        max_value=5,
        value=int(
            st.session_state["context_level" + current_chat + "value"]
        ),
        key="context_level" + current_chat,
        on_change=callback_fun,
        args=("context_level",),
    )
    st.caption(
        """
    If you need to set different context levels for different input sources,
    you can use this slider to set context levels.
    """
    )

with tap_model:
    set_paras_list = list(initial_content_all["paras"].keys())
    for paras_index, para_key in enumerate(set_paras_list):
        st.slider(
            label=set_paras_list[paras_index],
            min_value=initial_content_all["paras"][para_key]["min_value"],
            max_value=initial_content_all["paras"][para_key]["max_value"],
            value=int(
                st.session_state[para_key + current_chat + "value"]
            ),
            key=para_key + current_chat,
            on_change=callback_fun,
            args=(para_key,),
        )

with tap_func:
    st.button("Clear Chat", on_click=clear_button_callback)
    st.button("Delete All Chats", on_click=delete_all_chat_button_callback)

with st.expander("Additional Functions"):
    open_text_toolkit_button = st.button(
        label="Open Text Toolkit", key="open_text_toolkit_button"
    )
    if open_text_toolkit_button:
        st.session_state["open_text_toolkit"] = not st.session_state[
            "open_text_toolkit"
        ]
        save_set("open_text_toolkit")
        st.experimental_rerun()

    open_voice_toolkit_button = st.button(
        label="Open Voice Toolkit", key="open_voice_toolkit_button"
    )
    if open_voice_toolkit_button:
        st.session_state["open_voice_toolkit"] = not st.session_state[
            "open_voice_toolkit"
        ]
        save_set("open_voice_toolkit")
        st.experimental_rerun()

with st.container():
    input_user = st.text_area(
        label="Ask me anything...",
        value="",
        height=70,
        max_chars=4096,
        key="input_user",
    )
    st.text_area(
        label="",
        value="",
        height=5,
        max_chars=4096,
        key="output",
        disabled=True,
    )

with st.container():
    input_button = st.button(
        label="Submit",
        on_click=submit_question,
        args=(st.session_state["user_input_content"],),
    )

if st.session_state["user_voice_value"] != "":
    st.audio(
        voice_toolkit.tts_gpt(
            st.session_state["user_voice_value"], st.session_state["user_voice_value"]
        ),
        format="audio/mp3",
    )

with st.container():
    st.caption("Contexts:")
    st.caption("Previous messages:")
    for message in st.session_state["history" + current_chat]:
        if message["role"] == "user":
            st.text_area(
                label=f"User: {message['content']}",
                value="",
                height=3,
                max_chars=4096,
                key=f"input_context_{message['id']}",
                disabled=True,
            )
        elif message["role"] == "assistant":
            st.text_area(
                label=f"Assistant: {message['content']}",
                value="",
                height=3,
                max_chars=4096,
                key=f"output_context_{message['id']}",
                disabled=True,
            )

def clear_context():
    for message in st.session_state["history" + current_chat]:
        if message["role"] == "user":
            st.session_state[f"input_context_{message['id']}_value"] = ""
        elif message["role"] == "assistant":
            st.session_state[f"output_context_{message['id']}_value"] = ""

with st.container():
    st.button("Clear Context", on_click=clear_context)

st.experimental_rerun()

with st.container():
    st.text_area(
        label="Context Input",
        value=st.session_state["context_input" + current_chat + "value"],
        height=3,
        max_chars=4096,
        key="context_input",
        on_change=callback_fun,
        args=("context_input",),
    )

def input_callback():
    if st.session_state["user_input_area"] != "":
        user_input_content = st.session_state["user_input_area"]
        df_history = pd.DataFrame(st.session_state["history" + current_chat])
        if df_history.empty or len(df_history.query('role!="system"')) == 0:
            new_name = extract_chars(user_input_content, 18)
            reset_chat_name_fun(new_name)

with st.form("input_form", clear_on_submit=True):
    user_input = st.text_area(
        "**Input:**",
        key="user_input_area",
        help="Content will be displayed in Markdown format on the page. It's recommended to follow the language specifications, which is also beneficial for GPT's correct interpretation.",
        value=st.session_state["user_voice_value"],
    )
    submitted = st.form_submit_button(
        "Submit", use_container_width=True, on_click=input_callback
    )

if submitted:
    st.session_state["user_input_content"] = user_input
    st.session_state["user_voice_value"] = ""
    st.experimental_rerun()

# The remaining part of the code remains the same as in the original Chinese version.
# I have already translated and provided it in the previous response.


if st.session_state["user_input_content"] != "":
    if "r" in st.session_state:
        st.session_state.pop("r")
        st.session_state[current_chat + "report"] = ""
    st.session_state["pre_user_input_content"] = st.session_state["user_input_content"]
    st.session_state["user_input_content"] = ""
    # Temporary display
    show_each_message(
        st.session_state["pre_user_input_content"],
        "user",
        "tem",
        [area_user_svg.markdown, area_user_content.markdown],
    )
    # Model input
    history_need_input, paras_need_input = get_model_input()
    # Call the API
    with st.spinner("🤔"):
        try:
            if apikey := st.session_state["apikey_input"]:
                openai.api_key = apikey
            # Temporary API key configuration, records won't be stored in this case, suitable for public use
            elif "apikey_tem" in st.secrets:
                openai.api_key = st.secrets["apikey_tem"]
            # Note: When an API key is configured in st.secrets, chat records will be stored, even if this API key is not used
            else:
                openai.api_key = st.secrets["apikey"]
            r = openai.ChatCompletion.create(
                model=st.session_state["select_model"],
                messages=history_need_input,
                stream=True,
                **paras_need_input,
            )
        except (FileNotFoundError, KeyError):
            area_error.error(
                "Missing OpenAI API Key. Please configure Secrets after copying the project, or perform temporary configuration in the model options."
                "Details can be found in the [GitHub repository](https://github.com/PierXuY/ChatGPT-Assistant)."
            )
        except openai.error.AuthenticationError:
            area_error.error("Invalid OpenAI API Key.")
        except openai.error.APIConnectionError as e:
            area_error.error("Connection timeout. Please try again. Error:   \n" + str(e.args[0]))
        except openai.error.InvalidRequestError as e:
            area_error.error("Invalid request. Please try again. Error:   \n" + str(e.args[0]))
        except openai.error.RateLimitError as e:
            area_error.error("Request limit reached. Error:   \n" + str(e.args[0]))
        else:
            st.session_state["chat_of_r"] = current_chat
            st.session_state["r"] = r
            st.experimental_rerun()

# The rest of the code remains the same as in the original Chinese version.
# I have already translated and provided it in the previous responses.

if ("r" in st.session_state) and (current_chat == st.session_state["chat_of_r"]):
    if current_chat + "report" not in st.session_state:
        st.session_state[current_chat + "report"] = ""
    try:
        for e in st.session_state["r"]:
            if "content" in e["choices"][0]["delta"]:
                st.session_state[current_chat + "report"] += e["choices"][0]["delta"]["content"]
                show_each_message(
                    st.session_state["pre_user_input_content"],
                    "user",
                    "tem",
                    [area_user_svg.markdown, area_user_content.markdown],
                )
                show_each_message(
                    st.session_state[current_chat + "report"],
                    "assistant",
                    "tem",
                    [area_gpt_svg.markdown, area_gpt_content.markdown],
                )
    except ChunkedEncodingError:
        area_error.error("Network conditions are poor. Please refresh the page and try again.")
    # Handling 'stop' scenario
    except Exception:
        pass
    else:
        # Save content
        st.session_state["history" + current_chat].append(
            {"role": "user", "content": st.session_state["pre_user_input_content"]}
        )
        st.session_state["history" + current_chat].append(
            {"role": "assistant", "content": st.session_state[current_chat + "report"]}
        )
        write_data()
    # In case the user clicks 'stop' in the web page, in certain situations ss may temporarily be empty
    if current_chat + "report" in st.session_state:
        st.session_state.pop(current_chat + "report")
    if "r" in st.session_state:
        st.session_state.pop("r")
        st.experimental_rerun()

# The code for the user interface and other functionalities remains unchanged.
# I have already translated and provided it in the previous responses.


# Add event listener
v1.html(js_code, height=0)



