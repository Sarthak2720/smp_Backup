import { Menu, Search, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import logo from '../assets/logo.png';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState("");
    const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

    // Function to toggle mobile navbar
    const toggleNavbar = () => {
        setMobileDrawerOpen(!mobileDrawerOpen);
    };

    // Function to handle sending a message
    const handleSendMessage = () => {
        if (inputText.trim()) {
            const newMessage = { text: inputText, type: "sent" };
            setMessages((prevMessages) => [...prevMessages, newMessage]);

            // Check for specific user input and respond accordingly
            if (inputText.trim().toLowerCase() === "summarise chats with sonal") {
                const botResponse = {
                    text: `Here’s a summary of the chats with Sonal based on the provided images:

Initial Conversation:

- Sonal initiates the conversation with "Hi baby" and shares an Instagram post.
- The user responds with "Hello" and a thank you.

Emotional Expression:

- The user expresses deep affection, stating that they love Sonal very much, asking them to accept their love.
- They mention proposing to Sonal multiple times and ask for Sonal’s feelings.

Sonal's Response:

- Sonal remains non-committal, responding with "Okay" and "Nah" at first.
- Eventually, Sonal states they can't be in a relationship, saying "Sorry, but I can’t." They mention being focused on their career and unable to commit to a relationship.

User's Persistence:

- Despite Sonal's responses, the user tries to persuade them, stating they really love Sonal and would ask for confirmation one last time.
- The user expresses a lot of emotional pain, repeating that they care for Sonal deeply.

Final Outcome:

- Sonal stands firm, explaining that they don’t feel ready for a relationship and reiterate the need to focus on their career.
- The conversation ends with Sonal suggesting that the user should make their own decisions, while the user acknowledges that they will have to accept Sonal’s decision.

It’s a conversation filled with affection from the user and a polite but clear rejection from Sonal.`,
                    type: "received"
                };
                // Simulate a slight delay for bot response
                setTimeout(() => {
                    setMessages((prevMessages) => [...prevMessages, botResponse]);
                }, 1200);
            }

            setInputText("");
        }
    };

    // Add initial message after 0.9 second delay
    useEffect(() => {
        const initialMessage = { text: "Hello! How can I help you today?", type: "received" };
        const timer = setTimeout(() => {
            setMessages([initialMessage]);
        }, 900);

        // Cleanup timer on unmount
        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="flex flex-col h-screen w-full">
            {/* Header */}
            <header className='w-full bg-[#fffde7]'>
                <nav className='w-full flex justify-between items-center px-10 py-2'>
                    {/* Logo and Title */}
                    <div className='flex gap-5 items-center shrink-0'>
                        <img src={logo} alt="Logo" className='h-20 w-20' />
                        <h1 className='text-4xl font-bold font-[poppins]'>NIA</h1>
                    </div>

                    {/* Navigation Links */}
                    <div className='hidden lg:block'>
                        <ul className='flex gap-3'>
                            {["Today's NIA", "Careers", "Legacy", "Newsroom", "Library"].map((item, index) => (
                                <li
                                    key={index}
                                    className='text-lg font-bold hover:text-[#f22a53] hover:underline underline-offset-4 cursor-pointer'
                                >
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Search Bar */}
                    <div className='hidden relative hover:border-none searchdiv lg:flex items-center border border-black py-1'>
                        <div className='relative flex-1'>
                            <input
                                type='text'
                                className='bg-transparent cursor-pointer searchBar border-black px-3 py-2 w-full'
                                placeholder='Search'
                            />
                            <div className='absolute w-0 top-0 left-0 origin-left bg-[#f22a53] h-full'></div>
                        </div>
                        <div className='SearchIcon p-2 border-l-[0.25px] border-l-[#000]'>
                            <Search />
                        </div>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className='lg:hidden md:flex flex-col justify-end'>
                        <button onClick={toggleNavbar}>
                            {mobileDrawerOpen ? <X className='h-6 w-6' /> : <Menu className='h-6 w-6' />}
                        </button>
                    </div>

                    {/* Mobile Drawer */}
                    {mobileDrawerOpen && (
                        <div className='lg:hidden fixed top-[25vh] left-1/2 transform -translate-x-1/2 z-50 bg-white shadow-lg rounded-md p-5'>
                            <ul className='flex flex-col gap-4'>
                                {["Today's CIA", "Careers", "Legacy", "Newsroom", "Library"].map((item, index) => (
                                    <li
                                        key={index}
                                        className='text-lg font-bold hover:text-blue-500 cursor-pointer'
                                    >
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </nav>
            </header>

            {/* Chat Background */}
            <div className="flex-1 overflow-y-scroll p-4 chatbox bg-gray-100">
                <div className="flex flex-col space-y-4">
                    {messages.map((message, index) => (
                        <div
                            key={index}
                            className={`p-2 rounded-lg ${
                                message.type === 'sent'
                                    ? 'bg-blue-500 text-white self-end max-w-md'
                                    : 'bg-gray-300 text-gray-800 self-start max-w-md whitespace-pre-line'
                            }`}
                        >
                            {message.text}
                        </div>
                    ))}
                </div>
            </div>

            {/* Input Box */}
            <div className="bg-gray-200 bg-opacity-50 backdrop-blur p-4 flex items-center">
                <input
                    type="text"
                    className="flex-1 border border-gray-300 rounded-lg p-2 mr-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Type a message..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSendMessage();
                    }}
                />
                <button
                    className="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 transition duration-200"
                    onClick={handleSendMessage}
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
