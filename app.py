

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

st.set_page_config(page_title="ChatGPT Assistant", layout="wide", page_icon="🤖")
# 自定义元素样式
st.markdown(css_code, unsafe_allow_html=True)

if "initial_settings" not in st.session_state:
    # 历史聊天窗口
    st.session_state["path"] = "history_chats_file"
    st.session_state["history_chats"] = get_history_chats(st.session_state["path"])
    # ss参数初始化
    st.session_state["delete_dict"] = {}
    st.session_state["delete_count"] = 0
    st.session_state["voice_flag"] = ""
    st.session_state["user_voice_value"] = ""
    st.session_state["error_info"] = ""
    st.session_state["current_chat_index"] = 0
    st.session_state["user_input_content"] = ""
    # 读取全局设置
    if os.path.exists("./set.json"):
        with open("./set.json", "r", encoding="utf-8") as f:
            data_set = json.load(f)
        for key, value in data_set.items():
            st.session_state[key] = value
    # 设置完成
    st.session_state["initial_settings"] = True

with st.sidebar:
    st.markdown("# 🤖 聊天窗口")
    # 创建容器的目的是配合自定义组件的监听操作
    chat_container = st.container()
    with chat_container:
        current_chat = st.radio(
            label="历史聊天窗口",
            format_func=lambda x: x.split("_")[0] if "_" in x else x,
            options=st.session_state["history_chats"],
            label_visibility="collapsed",
            index=st.session_state["current_chat_index"],
            key="current_chat"
            + st.session_state["history_chats"][st.session_state["current_chat_index"]],
            # on_change=current_chat_callback  # 此处不适合用回调，无法识别到窗口增减的变动
        )
    st.write("---")


# 数据写入文件
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
     #Write new file
     write_data(new_name)
     # Transfer data
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
     st.text_input("Set window name:", key="set_chat_name", placeholder="Click to enter")
     st.selectbox(
         "Select model:", index=0, options=["gpt-3.5-turbo", "gpt-4"], key="select_model"
     )
     st.write("\n")
     st.caption(
         """
     - Double-click the page to directly locate the input field
     - Ctrl + Enter to quickly submit questions
     """
     )
     st.markdown(
         '<a href="https://github.com/PierXuY/ChatGPT-Assistant" target="_blank" rel="ChatGPT-Assistant">'
         '<img src="https://badgen.net/badge/icon/GitHub?icon=github&amp;label=ChatGPT Assistant" alt="GitHub">'
         "</a>",
         unsafe_allow_html=True,
     )
   # Download Data
if "history" + current_chat not in st.session_state:
     for key, value in load_data(st.session_state["path"], current_chat).items():
         if key == "history":
             st.session_state[key + current_chat] = value
         else:
             for k, v in value.items():
                 st.session_state[k + current_chat + "value"] = v

# Ensure that the page levels of different chats are consistent, otherwise the custom component will be re-rendered.
container_show_messages = st.container()
container_show_messages.write("")
# Dialogue display
with container_show_messages:
     if st.session_state["history" + current_chat]:
         show_messages(current_chat, st.session_state["history" + current_chat])

# Check if there are any conversations that need to be deleted
if any(st.session_state["delete_dict"].values()):
     for key, value in st.session_state["delete_dict"].items():
         try:
             deleteCount = value.get("deleteCount")
         exceptAttributeError:
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
     # Clicking New and Delete quickly in succession will trigger an error callback to increase judgment.
     if ("history" + current_chat in st.session_state) and (
         "frequency_penalty" + current_chat in st.session_state
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


# Input content display
area_user_svg = st.empty()
area_user_content = st.empty()
#Reply display
area_gpt_svg = st.empty()
area_gpt_content = st.empty()
# Error display
area_error = st.empty()

st.write("\n")
st.header("ChatGPT Assistant")
tap_input, tap_context, tap_model, tab_func = st.tabs(
     ["💬 Chat", "🗒️ Presets", "⚙️ Models", "🛠️ Features"]
)

with tap_context:
     set_context_list = list(set_context_all.keys())
     context_select_index = set_context_list.index(
         st.session_state["context_select" + current_chat + "value"]
     )
     st.selectbox(
         label="Select context",
         options=set_context_list,
         key="context_select" + current_chat,
         index=context_select_index,
         on_change=callback_fun,
         args=("context_select",),
     )
     st.caption(set_context_all[st.session_state["context_select" + current_chat]])

     st.text_area(
         label="Supplementary or custom context:",
         key="context_input" + current_chat,
         value=st.session_state["context_input" + current_chat + "value"],
         on_change=callback_fun,
         args=("context_input",),
     )

with tap_model:
     st.markdown("OpenAI API Key (optional)")
     st.text_input(
         "OpenAI API Key (optional)",
         type="password",
         key="apikey_input",
         label_visibility="collapsed",
     )
     st.caption(
         "This Key is only valid on the current web page and has a higher priority than the configuration in Secrets. It is only available to you and cannot be shared by others. [Official website](https://platform.openai.com/account/api-keys)"
     )

     st.markdown("Contains the number of conversations: ")
     st.slider(
         "Context Level",
         0,
         10,
         st.session_state["context_level" + current_chat + "value"],
         1,
         on_change=callback_fun,
         key="context_level" + current_chat,
         args=("context_level",),
         help="Indicates the number of historical conversations included in each session, and the default content is not counted.",
     )

     st.markdown("Model parameters:")
     st.slider(
         "Temperature",
         0.0,
         2.0,
         st.session_state["temperature" + current_chat + "value"],
         0.1,
         help="""Between 0 and 2, what sampling temperature should be used? Higher values (like 0.8) will make the output more random, while lower values (like 0.2) will make it more concentrated and Certainty.
           We generally recommend changing only one of this parameter or the top_p parameter, rather than both at the same time. """,
         on_change=callback_fun,
         key="temperature" + current_chat,
         args=("temperature",),
     )
     st.slider(
         "Top P",
         0.1,
         1.0,
         st.session_state["top_p" + current_chat + "value"],
         0.1,
         help="""An alternative to sampling with temperature is called "core probability-based" sampling. In this method, the model considers the predictions of the top_p tags with the highest probability.
           Therefore, when this parameter is 0.1, only markers including the top 10% probability mass will be considered. We generally recommend changing only one of this parameter or the sampling temperature parameter, rather than both at the same time. """,
         on_change=callback_fun,
         key="top_p" + current_chat,
         args=("top_p",),
     )
     st.slider(
         "Presence Penalty",
         -2.0,
         2.0,
         st.session_state["presence_penalty" + current_chat + "value"],
         0.1,
         help="""This parameter can take values from -2.0 to 2.0. Positive values penalize new tokens based on whether they appear in the currently generated text, thereby increasing the likelihood that the model will talk about new topics.""",
         on_change=callback_fun,
         key="presence_penalty" + current_chat,
         args=("presence_penalty",),
     )
    
    st.slider(
        "Frequency Penalty",
        -2.0,
        2.0,
        st.session_state["frequency_penalty" + current_chat + "value"],
        0.1,
        help="""该参数的取值范围为-2.0到2.0。正值会根据新标记在当前生成的文本中的已有频率对其进行惩罚，从而减少模型直接重复相同语句的可能性。""",
        on_change=callback_fun,
        key="frequency_penalty" + current_chat,
        args=("frequency_penalty",),
    )
    st.caption(
        "[官网参数说明](https://platform.openai.com/docs/api-reference/completions/create)"
    )

with tab_func:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("清空聊天记录", use_container_width=True, on_click=clear_button_callback)
    with c2:
        btn = st.download_button(
            label="导出聊天记录",
            data=download_history(st.session_state["history" + current_chat]),
            file_name=f'{current_chat.split("_")[0]}.md',
            mime="text/markdown",
            use_container_width=True,
        )
    with c3:
        st.button(
            "删除所有窗口", use_container_width=True, on_click=delete_all_chat_button_callback
        )

    st.write("\n")
    st.markdown("自定义功能：")
    c1, c2 = st.columns(2)
    with c1:
        if "open_text_toolkit_value" in st.session_state:
            default = st.session_state["open_text_toolkit_value"]
        else:
            default = True
        st.checkbox(
            "开启文本下的功能组件",
            value=default,
            key="open_text_toolkit",
            on_change=save_set,
            args=("open_text_toolkit",),
        )
    with c2:
        if "open_voice_toolkit_value" in st.session_state:
            default = st.session_state["open_voice_toolkit_value"]
        else:
            default = True
        st.checkbox(
            "开启语音输入组件",
            value=default,
            key="open_voice_toolkit",
            on_change=save_set,
            args=("open_voice_toolkit",),
        )

with tap_input:

    def input_callback():
        if st.session_state["user_input_area"] != "":
            # 修改窗口名称
            user_input_content = st.session_state["user_input_area"]
            df_history = pd.DataFrame(st.session_state["history" + current_chat])
            if df_history.empty or len(df_history.query('role!="system"')) == 0:
                new_name = extract_chars(user_input_content, 18)
                reset_chat_name_fun(new_name)

    with st.form("input_form", clear_on_submit=True):
        user_input = st.text_area(
            "**输入：**",
            key="user_input_area",
            help="内容将以Markdown格式在页面展示，建议遵循相关语言规范，同样有利于GPT正确读取，例如："
            "\n- 代码块写在三个反引号内，并标注语言类型"
            "\n- 以英文冒号开头的内容或者正则表达式等写在单反引号内",
            value=st.session_state["user_voice_value"],
        )
        submitted = st.form_submit_button(
            "确认提交", use_container_width=True, on_click=input_callback
        )
    if submitted:
        st.session_state["user_input_content"] = user_input
        st.session_state["user_voice_value"] = ""
        st.experimental_rerun()

    if (
        "open_voice_toolkit_value" not in st.session_state
        or st.session_state["open_voice_toolkit_value"]
    ):
        # 语音输入功能
        vocie_result = voice_toolkit()
        # vocie_result会保存最后一次结果
        if (
            vocie_result and vocie_result["voice_result"]["flag"] == "interim"
        ) or st.session_state["voice_flag"] == "interim":
            st.session_state["voice_flag"] = "interim"
            st.session_state["user_voice_value"] = vocie_result["voice_result"]["value"]
            if vocie_result["voice_result"]["flag"] == "final":
                st.session_state["voice_flag"] = "final"
                st.experimental_rerun()

def get_model_input():
     #History records to be entered
     context_level = st.session_state["context_level" + current_chat]
     history = get_history_input(
         st.session_state["history" + current_chat], context_level
     ) + [{"role": "user", "content": st.session_state["pre_user_input_content"]}]
     for ctx in [
         st.session_state["context_input" + current_chat],
         set_context_all[st.session_state["context_select" + current_chat]],
     ]:
         if ctx != "":
             history = [{"role": "system", "content": ctx}] + history
     # Set model parameters
     paras = {
         "temperature": st.session_state["temperature" + current_chat],
         "top_p": st.session_state["top_p" + current_chat],
         "presence_penalty": st.session_state["presence_penalty" + current_chat],
         "frequency_penalty": st.session_state["frequency_penalty" + current_chat],
     }
     return history, paras


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
     #Model input
     history_need_input, paras_need_input = get_model_input()
     # Call interface
     with st.spinner("🤔"):
         try:
             if apikey := st.session_state["apikey_input"]:
                 openai.api_key = apikey
             # Configure temporary apikey. Chat records will not be retained at this time and are suitable for public use.
             elif "apikey_tem" in st.secrets:
                 openai.api_key = st.secrets["apikey_tem"]
             # Note: When apikey is configured in st.secrets, chat records will be retained even if this apikey is not used.
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
                 "OpenAI API Key is missing, please configure Secrets after copying the project, or configure it temporarily in the model options."
                 "For details, see [Project Repository](https://github.com/PierXuY/ChatGPT-Assistant)."
             )
         except openai.error.AuthenticationError:
             area_error.error("Invalid OpenAI API Key.")
         except openai.error.APIConnectionError as e:
             area_error.error("Connection timed out, please try again. Error: \n" + str(e.args[0]))
         except openai.error.InvalidRequestError as e:
             area_error.error("Invalid request, please try again. Error: \n" + str(e.args[0]))
         except openai.error.RateLimitError as e:
             area_error.error("Request is restricted. Error: \n" + str(e.args[0]))
         else:
             st.session_state["chat_of_r"] = current_chat
             st.session_state["r"] = r
             st.experimental_rerun()

if ("r" in st.session_state) and (current_chat == st.session_state["chat_of_r"]):
     if current_chat + "report" not in st.session_state:
         st.session_state[current_chat + "report"] = ""
     try:
         for e in st.session_state["r"]:
             if "content" in e["choices"][0]["delta"]:
                 st.session_state[current_chat + "report"] += e["choices"][0]["delta"][
                     "content"
                 ]
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
         area_error.error("The network condition is not good, please refresh the page and try again.")
     # Deal with stop situations
     exceptException:
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
     # When the user clicks stop on the web page, ss will be temporarily empty in some cases.
     if current_chat + "report" in st.session_state:
         st.session_state.pop(current_chat + "report")
     if "r" in st.session_state:
         st.session_state.pop("r")
         st.experimental_rerun()

#Add event listener
v1.html(js_code, height=0)
