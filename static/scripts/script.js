const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatbtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");

let userMessage = null; // Variable to store user's message
const inputInitHeight = chatInput.scrollHeight;

function createChatLi(message, className) {
  const chatLi = document.createElement("li");
  chatLi.classList.add(className);
  chatLi.textContent = message;
  return chatLi;
}

const handleChat = () => {
  userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
  if (!userMessage) return;

  // Clear the input textarea and set its height to default
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Append the user's message to the chatbox on the right side
  const outgoingChatli = createChatLi(userMessage, "outgoing");
  outgoingChatli.classList.add("right-aligned");
  chatbox.appendChild(outgoingChatli);
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    // Display "Typing..." message while waiting for the response
    const incomingChatli = createChatLi("Typing...", "incoming");
    chatbox.appendChild(incomingChatli);
    const response = generateResponse(userMessage);
    incomingChatli.innerHTML = response;
  }, 600);
};

chatInput.addEventListener("input", () => {
  // Adjust the height of the input textarea based on its content
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
  // If Enter key is pressed without the Shift key and the window
  // width is greater than 800px, handle the chat
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

sendChatbtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () =>
  document.body.classList.remove("show-chatbot")
);
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);
// Function to generate response based on user's message
function generateResponse(userMessage) {
  let response = "";

  if (userMessage.toLowerCase().includes("hi") || userMessage.toLowerCase().includes("hello")) {
    response = "Hi! How may I assist you?";
  } else if (userMessage.toLowerCase().includes("help")) {
    response = "Sure! What do you need help with?";
  } else if (userMessage.toLowerCase().includes("water") && userMessage.toLowerCase().includes("crops")) {
    response = "The watering frequency depends on various factors like crop type, soil type, and weather conditions. Generally, most crops require regular watering, especially during dry periods. However, it's important to avoid overwatering as it can lead to waterlogging and root rot.";
  } else if (userMessage.toLowerCase().includes("pest") || userMessage.toLowerCase().includes("insect")) {
    response = "Pests can be a common problem in agriculture. Integrated pest management practices, such as crop rotation, using resistant varieties, and applying organic pesticides when necessary, can help control pest populations effectively.";
  } else if (userMessage.toLowerCase().includes("soil") && (userMessage.toLowerCase().includes("fertility") || userMessage.toLowerCase().includes("nutrient"))) {
    response = "Maintaining soil fertility is crucial for healthy crop growth. Practices like adding organic matter, using cover crops, and conducting soil tests can help improve soil fertility and ensure optimal nutrient levels.";
  } else if (userMessage.toLowerCase().includes("weed") && userMessage.toLowerCase().includes("control")) {
    response = "Weed control methods vary depending on the specific weed species and the crops being grown. Some common weed control techniques include hand weeding, mulching, and using herbicides. Integrated weed management approaches can be effective in long-term weed control.";
  } else if (userMessage.toLowerCase().includes("weather") && (userMessage.toLowerCase().includes("impact") || userMessage.toLowerCase().includes("crop"))) {
    response = "Weather conditions can significantly impact crop growth and yield. Extreme temperatures, drought, heavy rainfall, and storms can all affect crops differently. Implementing appropriate measures like irrigation, shelter, and adjusting planting schedules can help mitigate the impact of adverse weather conditions.";
  } else if (userMessage.toLowerCase().includes("sustainable") && userMessage.toLowerCase().includes("farming")) {
    response = "Sustainable farming practices aim to reduce environmental impact and promote long-term productivity. Some sustainable farming techniques include conservation tillage, crop rotation, water conservation, integrated pest management, and the use of organic fertilizers.";
  } else if (userMessage.toLowerCase().includes("technologies") && (userMessage.toLowerCase().includes("impact") || userMessage.toLowerCase().includes("agriculture"))) {
    response = "Our cutting-edge machine learning and deep learning technologies empower farmers to maximize their profits by providing valuable insights at every stage of the farming process. From making informed decisions to understanding demographic characteristics, identifying factors influencing crops, and implementing measures to maintain their health, our technologies contribute to a highly successful and rewarding harvest.";
  } else if (userMessage.toLowerCase().includes("benefits") && (userMessage.toLowerCase().includes("machine learning") || userMessage.toLowerCase().includes("deep learning"))) {
    response = "Farmers can gain numerous benefits from our machine learning and deep learning technologies. They can make informed decisions based on valuable insights, understand the demographic characteristics of their region, identify the factors influencing their crops, and implement measures to maintain crop health. By leveraging our technologies, farmers can maximize their profits and achieve highly successful harvests.";
  } else if (userMessage.toLowerCase().includes("help") && (userMessage.toLowerCase().includes("maximize") || userMessage.toLowerCase().includes("profits"))) {
    response = "Our technologies help farmers maximize their profits by providing them with valuable insights throughout the farming process. By making informed decisions, understanding the demographic characteristics of their region, identifying influential factors for their crops, and implementing measures to maintain crop health, farmers can optimize their operations and achieve highly successful harvests, leading to increased profits.";
  } else if (userMessage.toLowerCase().includes("suited") && (userMessage.toLowerCase().includes("conditions") || userMessage.toLowerCase().includes("strategy"))) {
    response = "We provide recommendations on the type of crops that are best suited for your respective conditions. By analyzing factors such as soil type, climate, and other relevant data, our machine learning and deep learning technologies can suggest crops that have higher chances of success in your specific conditions.";
  } else if (userMessage.toLowerCase().includes("fertilizer") && (userMessage.toLowerCase().includes("soil") || userMessage.toLowerCase().includes("crop"))) {
    response = "Our technologies can provide recommendations on the type of fertilizer that is best suited for your particular soil and crop. By considering factors such as soil composition, nutrient requirements of the crop, and other relevant data, we can suggest the most appropriate fertilizer to optimize the growth and health of your crops.";
  } else if (userMessage.toLowerCase().includes("predict") && (userMessage.toLowerCase().includes("yield ") || userMessage.toLowerCase().includes("location"))) {
    response = "We offer yield prediction capabilities as part of our technologies (currently in beta). By analyzing geographical locations, historical data, and other relevant factors, we can provide predictions on the yield per given area. This information can help farmers in planning and decision-making processes to optimize their productivity and maximize their harvests.";
  } else {
    // Default response if the user's message does not match any FAQ
    response = "I'm sorry, I don't have information on that topic. Please <a href='contact'>contact us</a> directly for personalized advice.";
  }

  return response;
}