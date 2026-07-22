function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

let button = document.getElementById('send-btn');
let isBotTyping
let selectedFile = null
let userinput = document.getElementById('user-input');
const image = document.getElementById('imageUpload').files[0];

function showImage(event) {
    const input = event.target;
    const preview = document.getElementById('preview')
    const wrapper = document.getElementById('preview-wrapper')

    if (input.files && input.files[0]) {
        selectedFile = input.files[0]

        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            wrapper.style.display = 'block';
        }
        reader.readAsDataURL(selectedFile)
    }
}

async function updateUserdata(role, text, productIds = null) {
    if ((text === undefined || text === null || text === '') && !productIds) {
        return;
    }
    const url = '/chatbot/'
    const formData = new FormData()
    formData.append('role', role)
    formData.append('message', text || '')

    if (selectedFile) {
        formData.append('user_image', selectedFile)
    }
    if (productIds) {
        formData.append('product_ids', JSON.stringify(productIds));
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            credentials: 'include',
            headers: { 'X-CSRFToken': getCSRFToken() },
            body: formData
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    }
    catch (error) {
        console.log("Error", error.message)
        return null
    }
}
async function ragUpdate(role, text) {
    if (!text || !text.trim()) {
        return null;
    }
    const url = '/chatbot/ragchat/'
    const formData = new FormData()
    formData.append('role', role)
    formData.append('message', text)
    // console.log('formdata', formData)
    try {
        const ragresponse = await fetch(url, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });
        if (!ragresponse.ok) {
            throw new Error(`HTTP error! Status: ${ragresponse.status}`)
        }
        // console.log('body', body)
        const data = await ragresponse.json();
        console.log('RAG Response:', data);
        return data
    }
    catch (error) {
        console.log("Error", error.message)
        return null
    }
}

async function fetchChat() {
    const url = '/chatbot/chathistory/'

    try {
        const response = await fetch(url, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`)
        }
        const chat = await response.json();
        return chat
    }
    catch (error) {
        console.log("Error", error.message)
        return null
    }
}
async function renderallmessages() {
    const chat = await fetchChat()
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = "";

    for (let msg of chat) {
        let placemessage = document.createElement('div');
        placemessage.classList.add('message');

        if (msg['role'] === 'user') {
            placemessage.classList.add('user');
            if (!msg['user_image']) {
                placemessage.textContent = msg['message'];
            } else {
                placemessage.innerHTML = `<img src="${msg['user_image']}" style="max-width:150px;border-radius:8px;margin-bottom:6px;"> <br> ${msg.message}`;
            }
            chatMessages.appendChild(placemessage);
        } else {
            placemessage.classList.add('assistant');
            if (msg['message']) {
                placemessage.textContent = msg['message'];
                chatMessages.appendChild(placemessage);
            }
            if (msg['product_ids'] && msg['product_ids'].length > 0) {
                const { container } = await productrender(msg['product_ids']);
                chatMessages.appendChild(container);
            }
        }
    }

    scrollChatToBottom();
}

function showTypingIndicator(show) {
    const chatMessages = document.getElementById('chat-messages');
    let typingEl = document.getElementById('typing-indicator');

    if (show) {
        if (!typingEl) {
            typingEl = document.createElement('div');
            typingEl.id = 'typing-indicator';
            typingEl.classList.add('message', 'assistant');
            typingEl.textContent = 'Please wait...';
            chatMessages.appendChild(typingEl);
        }
    } else {
        if (typingEl) typingEl.remove();
    }
    scrollChatToBottom();
}

async function retrieveProducts(product_ids) {
    const idString = Array.isArray(product_ids)
        ? product_ids.join(',')
        : String(product_ids).replace(/[\[\]\s]/g, '');

    const url = `/shop/api/products/${idString}`

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'content-type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`)
        }
        const productdata = await response.json();
        return productdata
    }
    catch (error) {
        console.log("Error", error.message)
        return null
    }
}
async function productrender(productIds) {
    const container = document.createElement('div');
    container.classList.add('product-grid');

    if (!productIds || productIds.length === 0) {
        return { container };
    }

    const productData = await retrieveProducts(productIds);

    if (!productData || !productData.length) {
        return { container };
    }

    container.innerHTML = productData.map(product => `
        <div class="chat-product-card">
            <img src="${product.image}" alt="${product.product_name}" loading="lazy">
            <div class="product-info">
                <h6>${product.product_name}</h6>
                <p class="price">₹${product.price}</p>
                <a href="/shop/products/${product.id}/" class="btn btn-sm btn-primary">View</a>
            </div>
        </div>
    `).join('');

    return { container };
}

async function userbotmessage() {
    let text = userinput.value
    if (text.trim() != '') {
        await updateUserdata('user', text)
        await renderallmessages()
        selectedFile = null
        document.getElementById('user-input').value = ''
        document.getElementById('imageUpload').value = ''
        document.getElementById('preview-wrapper').style.display = 'none'
        await getBotReplies(text)
    }
    else {
        return;
    }
}
async function getBotReplies(text) {
    try {
        isBotTyping = true;
        showTypingIndicator(true)

        const ragData = await ragUpdate('assistant', text)
        isBotTyping = false;
        showTypingIndicator(false)

        const answerText = ragData?.answer || ""
        const productIds = ragData?.product_ids || [];

        if (answerText.trim() !== "") {
            await updateUserdata('assistant', answerText)
        }
        if (productIds.length > 0) {
            await updateUserdata('assistant', '', productIds)
        }

        await renderallmessages();
    }
    catch (error) {
        console.error(error);
        isBotTyping = false;
        showTypingIndicator(false);
        await updateUserdata('assistant', 'Something went wrong');
        await renderallmessages();
    }
}

function scrollChatToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

button.addEventListener("click", async function () {
    await userbotmessage()
})

userinput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        button.click();
    }
})

let chat_toggle = document.getElementById('chat-toggle')
let chatcontainer = document.getElementById('chat-container')
let chatclose = document.getElementById('chat-close')
function toggleChat() {
    chatcontainer.classList.toggle('open')
}

function toggleChatclose() {
    chatcontainer.classList.remove('open')
}
let removeimage = document.getElementById('remove-image')
let previewWrapper = document.getElementById('preview-wrapper')
function removeimagefn() {
    previewWrapper.style.display = 'none'
    document.getElementById('imageUpload').value = ''
    selectedFile = null
}
removeimage.addEventListener("click", removeimagefn)

chat_toggle.addEventListener("click", toggleChat)
chatclose.addEventListener("click", toggleChatclose)
document.getElementById("imageUpload").addEventListener("change", showImage);

renderallmessages()
async function ensureSession() {
    await fetch('/chatbot/chathistory/', { method: 'GET', credentials: 'include' });
}
ensureSession().then(() => renderallmessages());