# 🤖 ChatGPT-Assistant
The ChatGPT conversation assistant built on Streamlit is easy to use, not easy to disconnect, and supports the following functions:
- Multiple chat windows
- Preservation of historical conversations
- Default chat context
- Model parameter adjustment
- Export conversations as Markdown files
- ChatGPT voice communication (Edge browser on computer recommended)
## 🤩 [Deployed Project](https://pearxuy-gpt.streamlit.app/)
- To directly use the deployed project, you can configure the Openai Key in the settings options of the web page. At this time, historical conversations will not be retained. It is only valid in the user's current session and will not be shared by others.
- Deploy the project by yourself. After configuring the Openai Key in Secrets, historical conversation records will be retained. At this time, it needs to be set as a private application to create a personal GPT assistant.

### skills:
- Double-click the page to directly locate the input field
- Ctrl + Enter to quickly submit questions

# deploy

## Streamlit Cloud deployment (recommended)
It is easy and free to deploy and can be used without having to access the Internet. Please note that it is set as a private application.
Please refer to the [detailed steps](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/Tutorial.md) provided by [@Hannah11111](https://github.com/Hannah11111).
1. `Fork` this project to your personal Github repository.
2. Register a [Streamlit Cloud account](https://share.streamlit.io/) and connect to Github.
3. Start deploying the application. For details, please refer to the [official tutorial](https://docs.streamlit.io/streamlit-community-cloud/get-started).
4. Configure Openai Key in the Secrets of the application. Please refer to the figure below for the specific format:
<div style="display: flex;">
   <img src="https://github.com/PierXuY/ChatGPT-Assistant/blob/main/Figure/advanced-setting.png" alt="advanced-setting.png" style="flex: 1; width: 40 %;"/>
   <img src="https://github.com/PierXuY/ChatGPT-Assistant/blob/main/Figure/set-apikey.png" alt="set-apikey.png" style="flex: 1; width: 40 %;" />
</div>
You can also configure it after deployment is complete.

## Local deployment
1. Establish a virtual environment (recommended)

2. Clone the project (you can also manually download it locally)
```bash
git clone https://github.com/PierXuY/ChatGPT-Assistant.git
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set API Key; set API Base (optional)

- Write `apikey = "Openai Key"` in the `.streamlit/secrets.toml` file
- Write the proxy interface in the `.streamlit/secrets.toml` file to achieve scientific use. The format is `apibase = "agent interface address"`, and the description is as follows:
   1. You can directly use the proxy interface established by the project [openai-forward](https://github.com/beidongjiedeguang/openai-forward), that is, `apibase = "https://api.openai-forward.com/v1 "`.
   2. You can refer to the [openai-forward](https://github.com/beidongjiedeguang/openai-forward) project to build the proxy interface and set it up yourself.

5. Start the application
```bash
streamlit run app.py
```

# illustrate
- The user name and SVG format avatar can be customized in the [custom.py](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/libs/custom.py) file [(source)](https: //www.dicebear.com/playground?style=identicon).
- Edit [set_context.py](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/libs/set_context.py) in the deployed project source code to add preset context options. Automatically syncs to the app.
- If possible, you can consider changing the file reading and writing logic in [helper.py](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/libs/helper.py) to cloud database operations to prevent History is lost.


# Acknowledgments
- The earliest modification was based on the [shan-mx/ChatGPT_Streamlit](https://github.com/shan-mx/ChatGPT_Streamlit) project, thank you.
- The default [Context Function](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/set_context.py) is referenced from [binary-husky/chatgpt_academic](https://github.com/binary -husky/chatgpt_academic) project and [f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) project, thanks.
- The voice interaction function refers to the projects [talk-to-chatgpt](https://github.com/C-Nedelcu/talk-to-chatgpt) and [Voice Control for ChatGPT](https://chrome.google.com /webstore/detail/voice-control-for-chatgpt/eollffkcakegifhacjnlnegohfdlidhn) implementation, thanks.
- The local science-free Internet access function can use the project [openai-forward](https://github.com/beidongjiedeguang/openai-forward), thank you.
