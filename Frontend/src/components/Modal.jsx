// Modal.jsx
import React from 'react';

const Modal = ({ children, onClose }) => {
    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white rounded-lg p-6 w-[30vw]">
                {children}
                <button
                    className="absolute top-2 right-2 text-gray-500"
                    onClick={onClose}
                >
                    &times;
                </button>
            </div>
        </div>
    );
};

export default Modal;