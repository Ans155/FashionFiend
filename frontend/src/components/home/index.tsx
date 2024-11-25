import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";

const initialMessages = [
    { text: "What is Coast Fire Age?", emoji: "🏖️" },
    { text: "Can we switch the health insurance policy to increase cover?", emoji: "🏥" },
    { text: "How to switch mutual funds?", emoji: "💹" },
    { text: "How do I decide the inflation % to be put in FIRE calculation?", emoji: "🔥" },
];

const Home: React.FC = () => {
    const [question, setQuestion] = useState("");
    const navigate = useNavigate();
    const dispatch = useDispatch();

    const handleSubmit = async () => {
        if (question.trim()) {
            const chatId = "123";
            navigate(`/chat/${chatId}`, {
                state: { initialMessage: question },
            });
        }
    };

    const handleCardClick = async (question: string) => {
        const chatId = "123";
        if (chatId) {
            navigate(`/chat/${chatId}`, {
                state: { initialMessage: question },
            });
        }
    };

    return (
        <div className="flex flex-col bg-gray-900 text-gray-100 min-h-screen">
            <main className="flex-grow p-6 md:p-12 lg:p-16 xl:p-24">
                <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">Welcome to FashionFiend</h1>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12 mt-6">
                    {initialMessages.map((message, index) => (
                        <div
                            key={index}
                            onClick={() => handleCardClick(message.text)}
                            className="bg-gray-800 p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-pointer"
                        >
                            <div className="text-4xl mb-4">{message.emoji}</div>
                            <p className="text-sm md:text-base">{message.text}</p>
                        </div>
                    ))}
                </div>

                <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                    <textarea
                        id="message"
                        className="w-full h-32 bg-gray-700 text-gray-100 rounded-lg p-4 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Ask me anything..."
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                    ></textarea>
                    <button
                        onClick={handleSubmit}
                        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center transition-colors duration-300"
                    >
                        <span className="mr-2">➤</span>
                        Send
                    </button>
                </div>
            </main>
        </div>
    );
};

export default Home;

