import React, { useState } from "react";
import Navbar from "../Navbar/Navbar";
import {
  PageContainer,
  ImageSection,
  ColorSection,
  ProfileButton,
  NameButton,
  IDButton,
  SeedNumButtonContainer,
  SeedNumButton,
  QuestionButton,
  AnswerImg
} from "./MyBasic";
import bgImage from "../../assets/images/MyPageBG.svg";
import profileImage from "../../assets/images/MyProfile.svg";
import AnswerImage from "../../assets/images/Answer.svg";

const MyBasic: React.FC = () => {
  const [showAnswer, setShowAnswer] = useState(false);

  const handleQuestionClick = () => {
    setShowAnswer(true);
    setTimeout(() => {
      setShowAnswer(false);
    }, 3000);
  };

  return (
    <PageContainer>
      <Navbar />
      <ImageSection bgImage={bgImage}>
        <ProfileButton
          image={profileImage}
          onClick={() => console.log("Profile button clicked!")}
        />
        <NameButton onClick={() => console.log("Name button clicked!")}>
          박예은
        </NameButton>
        <IDButton onClick={() => console.log("ID button clicked!")}>
          _.zer023
        </IDButton>
        <SeedNumButtonContainer>
          <SeedNumButton
            onClick={() => console.log("SeedNum button clicked!")}
          />
          <QuestionButton onClick={handleQuestionClick} />
          {showAnswer && <AnswerImg src={AnswerImage} alt="Answer" />}
        </SeedNumButtonContainer>
      </ImageSection>
      <ColorSection></ColorSection>
    </PageContainer>
  );
};

export default MyBasic;
