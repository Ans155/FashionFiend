import React, { useState, useEffect, useRef } from "react";
import { useParams, useLocation } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
import Loader from "../loader";
import { sendMessageToAPI } from "../../api/chat";
import "../chat/index.css";

const Chat: React.FC = () => {
    const { chatId } = useParams<{ chatId: string }>();
    const location = useLocation();
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const [initialMessage, setInitialMessage] = useState(
        location.state?.initialMessage || null
    );
    const initialMessageSentRef = useRef(false);
    const profile_logo = "/assets/logo/user.svg";
    const gpt_logo = "/assets/gpt.svg";
    const send_icon = "/assets/icon/send.svg";
    const [previewImages, setPreviewImages] = useState<string[]>([]);

    useEffect(() => {
        if (initialMessage && !initialMessageSentRef.current) {
            handleSendMessage(initialMessage, Date.now());
            initialMessageSentRef.current = true;
            window.history.replaceState({}, "");
        }
    }, [initialMessage]);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTo({
                top: chatContainerRef.current.scrollHeight,
                behavior: "smooth",
            });
        }
    }, [messages]);

    useEffect(() => {
        const fetchImages = async () => {
            const images = await Promise.all(
                messages.flatMap((message) => 
                    message.content.products?.map((product:any) => fetchPreviewImage(product.url)) || []
                )
            );
            setPreviewImages(images);
        };

        fetchImages();
    }, [messages]);

    const handleSendMessage = async (question: string, messageId: number) => {
        setLoading(true);
        try {
            const response = await sendMessageToAPI(question, messageId);
            setMessages((prevMessages) => [
                ...prevMessages,
                {
                    role: "ai",
                    content: {
                        message: response.answer?.recommendation_text,
                        products: response.answer?.products,
                    },
                    _id: response.messageId || messageId,
                },
            ]);
        } catch (error) {
            console.error("Error handling message:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim()) {
            const newMessage = {
                role: "user",
                content: { message: input },
                _id: Date.now(),
            };
            setMessages((prevMessages) => [...prevMessages, newMessage]);
            await handleSendMessage(input, newMessage._id);
            setInput("");
        }
    };

    const fetchPreviewImage = async (url: string) => {
        try {
            const response = await fetch(
                `https://api.microlink.io?url=${encodeURIComponent(url)}`
            );
            const data = await response.json();
            return data?.data?.image?.url || null; // Return Open Graph image or null
        } catch (error) {
            console.error("Error fetching preview image:", error);
            return null;
        }
    };

    const renderProductRecommendations = (products: any[], previewImages: string[]) => {
      return (
        <div className="grid sm:grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {products.map((product, index) => (
            <div
              key={index}
              className="flex flex-col bg-gray-800 rounded-lg overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20"
            >
              {previewImages[index] && (
                <div className="relative h-48 w-full bg-gray-700">
                  <img
                    src={previewImages[index]}
                    alt={product.name}
                    className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                    onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
                      e.currentTarget.src = "/assets/placeholder.png";
                    }}
                  />
                </div>
              )}
              <div className="p-4 flex flex-col flex-grow">
                <h3 className="font-medium text-gray-200 text-lg mb-2 line-clamp-2">
                  {product.name}
                </h3>
                <a
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-auto bg-blue-600 text-white py-2 px-4 text-center rounded-md hover:bg-blue-700 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                >
                  View Product
                </a>
              </div>
            </div>
          ))}
        </div>
      );
    };
    

    return (
        <div className="flex flex-col bg-gray-900 w-full lg:px-[100px] md:py-[40px] md:px-[20px] px-[5px] text-white">
            <div
                className="flex flex-col py-2 md:px-4 px-1 md:h-[66vh] h-[75vh] overflow-y-auto"
                ref={chatContainerRef}
            >
                {messages.map((message, index) => (
                    <div key={index} className="mb-4">
                        <div className="flex flex-row font-sf-pro font-medium">
                            {message.role === "user" && (
                                <>
                                    <img
                                        src={profile_logo}
                                        alt="User Logo"
                                        className="md:h-8 h-6 flex md:mt-1 mt-2 rounded-[20px] mr-2"
                                    />
                                    <div className="p-2 bg-gray-900 text-white">
                                        {message.content.message}
                                    </div>
                                </>
                            )}
                            {message.role === "ai" && (
                                <>
                                    <img
                                        src={gpt_logo}
                                        alt="GPT Logo"
                                        className="md:h-8 h-6 flex md:mt-5 mt-6"
                                    />
                                    <div className="font-sf-pro self-end bg-gray-900 p-4 text-[17px]">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            rehypePlugins={[rehypeSanitize]}
                                            className="markdown-body text-[15px]"
                                        >
                                            {message.content.message}
                                        </ReactMarkdown>
                                        {message.content.products &&
                                            renderProductRecommendations(
                                                message.content.products,
                                                previewImages
                                            )}
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="relative">
                        <Loader />
                    </div>
                )}
            </div>
            <form
                className="sticky bottom-0 bg-gray-900"
                onSubmit={handleSubmit}
            >
                <div className="flex flex-row items-center relative">
                    <input
                        type="text"
                        className="w-full pl-[12px] py-[16px] pr-[44px] border border-gray-300 rounded-[12px] focus:outline-none text-black"
                        placeholder="Ask me anything..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                    />
                    <button
                        type="submit"
                        className="absolute right-3 top-1/2 transform -translate-y-1/2"
                    >
                        <img
                            src={send_icon}
                            alt="Send Icon"
                            className="h-8 w-8 rotate-90"
                        />
                    </button>
                </div>
                <div className="font-sf-pro flex justify-center items-center py-[6px] text-center md:text-[14px] text-[12px] text-[#999999]">
                    FashionFiend may make mistakes, so double-check its
                    responses.
                </div>
            </form>
        </div>
    );
};

export default Chat;
