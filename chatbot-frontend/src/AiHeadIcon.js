// In AiHeadIcon.js
import React from 'react';
import aiHeadImage from './DALL_E.png'; // Update the import path if the image is in a different directory

const AiHeadIcon = () => {
  return (
    <img src={aiHeadImage} alt="AI Head Icon" style={{ width: '50px', height: 'auto' }} />
  );
};

export default AiHeadIcon;
