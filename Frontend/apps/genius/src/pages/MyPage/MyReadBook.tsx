import React, { useState, useEffect } from "react";
import axios from "axios";
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
  AnswerImg,
  ReadBookTitleImage,
  TextBoxContainer,
  TextBox,
  BookImageContainer,
  BookImage,
  LeftButton,
  NextPageButton
} from "./MyReadBook";
import bgImage from "../../assets/images/MyPageBG.svg";
import AnswerImage from "../../assets/images/Answer.svg";
import ReadBookTitleImageSrc from "../../assets/images/ReadBookTitleImage.svg";

const MyReadBook: React.FC = () => {
  const [showAnswer, setShowAnswer] = useState(false);
  const [profileImage, setProfileImage] = useState<string>('');
  const [nickname, setNickname] = useState<string>('');
  const [email, setEmail] = useState<string>('');

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const user = localStorage.getItem("user");
        if (user) {
          const userData = JSON.parse(user);
          const userId = userData.id;

          // API 호출하여 프로필 정보 가져오기
          const response = await axios.get(`http://localhost:8000/genius/members/${userId}/`);
          const member = response.data;
          setProfileImage(member.profImg);
          setNickname(member.nickname);
          setEmail(member.email);
        } else {
          console.error("No user found in localStorage");
        }
      } catch (error) {
        console.error("Error fetching profile data:", error);
      }
    };

    fetchProfileData();
  }, []);

  const handleQuestionClick = () => {
    setShowAnswer(true);
    setTimeout(() => {
      setShowAnswer(false);
    }, 3000);
  };

  const handleImageClick = (type: string) => {
    console.log(` ${type}`);
  };

  return (
    <PageContainer>
      <Navbar />
      <ImageSection bgImage={bgImage}>
        <ProfileButton
          image={profileImage || 'default_profile_image_url'} // 기본 이미지 설정
          onClick={() => console.log("Profile button clicked!")}
        />
        <NameButton onClick={() => console.log("Name button clicked!")}>
          {nickname || "이름"}
        </NameButton>
        <IDButton onClick={() => console.log("ID button clicked!")}>
          {email || "Email"}
        </IDButton>
        <SeedNumButtonContainer>
          <SeedNumButton
            onClick={() => console.log("SeedNum button clicked!")}
          />
          <QuestionButton onClick={handleQuestionClick} />
          {showAnswer && <AnswerImg src={AnswerImage} alt="Answer" />}
        </SeedNumButtonContainer>
      </ImageSection>
      <ColorSection>
        <ReadBookTitleImage src={ReadBookTitleImageSrc} alt="Read Book Title" />
        <BookImageContainer>
          <BookImage onClick={() => handleImageClick("BookImage")} />
          <LeftButton onClick={() => console.log("LeftButton clicked!")} />
          <NextPageButton onClick={() => console.log("NextPageButton clicked!")} />
        </BookImageContainer>
        <TextBoxContainer>
          <TextBox>
            김미미는 갈색 머리에 까만 눈을 가지고 있어요. 미미는 매우 용감한 성격을 가진 소녀예요.
          </TextBox>
        </TextBoxContainer>
      </ColorSection>
    </PageContainer>
  );
};

export default MyReadBook;
