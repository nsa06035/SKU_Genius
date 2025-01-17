import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
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
  SampleButton,
  ButtonRow,
  HoverButton
} from "./MyPageBook";
import bgImage from "../../assets/images/MyPageBG.svg";
import AnswerImage from "../../assets/images/Answer.svg";
import BookTextImage from "../../assets/images/BookTitle.svg";
import AddButtonImg1 from "../../assets/images/BookChoose1.svg";
import AddButtonImg2 from "../../assets/images/BookChoose2.svg";
import ButtonImage1 from "../../assets/images/BookSample.svg";
import ButtonImage2 from "../../assets/images/BookSample2.svg";
import ButtonImage3 from "../../assets/images/BookSample3.svg";

const MyPageBook: React.FC = () => {
  const navigate = useNavigate();
  const [profileImage, setProfileImage] = useState<string>('');
  const [nickname, setNickname] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [showAnswer, setShowAnswer] = useState(false);
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  const buttonImages = [ButtonImage1, ButtonImage2, ButtonImage3];

  useEffect(() => {
    const fetchMemberData = async () => {
      const user = localStorage.getItem("user");
      if (user) {
        const userData = JSON.parse(user);
        const userId = userData.id; // 로그인한 사용자의 ID를 가져옵니다.

        try {
          const response = await axios.get(`http://localhost:8000/genius/members/${userId}/`);
          const member = response.data;
          setProfileImage(member.profImg);
          setNickname(member.nickname);
          setEmail(member.email);
        } catch (error) {
          console.error("Error fetching member data:", error);
        }
      } else {
        console.error("No user found in localStorage");
      }
    };

    fetchMemberData();
  }, []);

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
          image={profileImage || 'default_profile_image_url'} // Fallback image URL if profileImage is not available
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
      <ButtonRow>
        {buttonImages.map((image, index) => (
          <SampleButton
            key={index}
            bgImage={image}
            onMouseEnter={() => setHoverIndex(index + 1)}
            onMouseLeave={() => setHoverIndex(null)}
          >
            {hoverIndex === index + 1 && (
              <>
                <HoverButton
                  bgImage={AddButtonImg1}
                  style={{ opacity: 1, transform: "translate(-70%, -120%)" }}
                  onClick={() => navigate("/MyReadBook")} // 클릭 시 페이지 이동
                />
                <HoverButton
                  bgImage={AddButtonImg2}
                  style={{ opacity: 1, transform: "translate(70%, -120%)" }}
                  onClick={() => navigate("/MyReadBook")} // 클릭 시 페이지 이동
                />
              </>
            )}
          </SampleButton>
        ))}
      </ButtonRow>
      <ColorSection>
        <div
          style={{
            width: "100%",
            display: "flex",
            justifyContent: "flex-start",
            alignItems: "flex-start",
            height: "100%",
            padding: "20px"
          }}
        >
          <img
            src={BookTextImage}
            alt="Book Text"
            style={{
              maxWidth: "100%",
              maxHeight: "100%",
              height: "auto",
              margin: "-50px 0 0 -20px"
            }}
          />
        </div>
      </ColorSection>
    </PageContainer>
  );
};

export default MyPageBook;
