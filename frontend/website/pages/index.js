import Head from "next/head";
import "bootstrap/dist/css/bootstrap.min.css";
import SearchResult from "../components/searchresult";
import jsCookie from "js-cookie";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import InfiniteScroll from "react-infinite-scroll-component";
import React, { useEffect, useState } from "react";
import { Paper, Button, IconButton, Skeleton, Tooltip, Typography } from "@mui/material";
import { ArrowUpwardOutlined } from "@mui/icons-material";
import { Router, useRouter } from "next/router";
import QuickSubmissionBox from "../components/quickSubmissionBox";
import Setup from "./setup";
import dynamic from "next/dynamic";
import useUserDataStore from "../store/userData";
import { BASE_URL_CLIENT, BASE_URL_SERVER, RECENTLY_ACCESSED_SUB_ENDPOINT, 
        COMMUNITIES_ENDPOINT, RECOMMEND_COMMUNITIES_ENDPOINT, 
        WEBSITE_SEARCH_ENDPOINT} from "../static/constants";
import RecommendedCommunityBox from "../components/recommendedCommunityBox";

const HomeConnections = dynamic(() => import("./homeconnections"), {
  ssr: false,
});

function Home({ data, community_joined_data, recently_accessed_submissions, recommendedCommunitiesData }) {
  const router = useRouter();
  const [items, setItems] = useState(data.search_results_page);
  const [page, setPage] = useState(parseInt(data.current_page) + 1);
  const [latestRecommendationId, setLatestRecommendationId] = useState(data.search_id)
  const [endOfRecommendations, setEndOfRecommendations] = useState((data.search_results_page.length) < 10)
  const [userOwnSubmissions, setUserOwnSubmissions] = useState(null);

  const [onboardingStep, setOnboardingStep] = useState(0);
  let extensionId = "aafcjihpcjlagambenogkhobogekppgp";
  let imgSrc = "/tree48.png";

  const { userCommunities, user_id, setUserDataStoreProps } = useUserDataStore();

  let homePageContent = <Setup head="Onboarding" updateStep={onboardingStep}></Setup>;

  function checkExtension() {
    const isImagePresent = new Promise((resolve, _) => {
      const img = new Image();
      img.src = "chrome-extension://" + extensionId + imgSrc;
      img.onload = () => {
        resolve(true);
      }
      img.onerror = () => {
        resolve(false);
      }
    });
    return isImagePresent;
  }

  async function checkOnboarding() {
    const img = await checkExtension();
    if (!img) {
      if (community_joined_data.community_info.length > 0 || community_joined_data.followed_community_info.length > 0) {
        if (recently_accessed_submissions && recently_accessed_submissions.length >= 1) {
          setOnboardingStep(0);
        } else {
          setOnboardingStep(3);
        }
      }
      else {
        setOnboardingStep(1);
      }
    } else {
      if (community_joined_data.community_info.length > 0 || community_joined_data.followed_community_info.length > 0) {
        if (!(endOfRecommendations && items.length > 0)) {
          //if user has created community but no submission
          setOnboardingStep(3);
        }
      } else {
        setOnboardingStep(2);
      }
    }
  }

  async function getVizData() {
    var searchURL = BASE_URL_CLIENT + WEBSITE_SEARCH_ENDPOINT;
    searchURL += "?own_submissions=True" + "&community=all&visualize=True";
    const users_submissions = await fetch(searchURL, {
      headers: new Headers({
        Authorization: jsCookie.get("token"),
      }),
    });

    if (users_submissions.status == 200) {
      const user_own_submissions = await users_submissions.json();
      setUserOwnSubmissions(user_own_submissions);
      return user_own_submissions
    }
    else {
      setUserOwnSubmissions(null);
      return null;
    }

  }

  useEffect(async () => {
    await checkOnboarding();
    setUserDataStoreProps({ userCommunities: community_joined_data.community_info });
    // get viz data
    //var temp = await getVizData();
    console.log('received vizdata!');

  }, []);

  const handleIndexFinish = (data) => {
    window.location.reload();
  }

  if (onboardingStep > 0) {
    homePageContent = <Setup head="Onboarding" updateStep={onboardingStep} setupFinish={handleIndexFinish}></Setup>;
  }

  const fetchNextPage = async () => {
    let pg = page
    var recommendationURLClient = BASE_URL_CLIENT + WEBSITE_SEARCH_ENDPOINT;
    try {
      const response = await fetch(
        `${recommendationURLClient}?search_id=${latestRecommendationId}&page=${page}`,
        {
          headers: new Headers({
            Authorization: jsCookie.get("token"),
          }),
        }
      );
      const content = await response.json();
      var tempItems = content.recommendation_results_page
      if (tempItems < 10) {
        setEndOfRecommendations(true)
      }
      setItems([...items, ...tempItems]);
      pg += 1
      setPage(pg)
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    if (page) {
      console.log("On page no:", page);
    }
  }, [page])

  useEffect(() => {
  }, [latestRecommendationId])


  useEffect(() => {
  }, [endOfRecommendations])

  // code to add a 'scroll to top of page' sticky button that is visible once user scrolls down
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset;
      const buffer = 250
      if (scrollTop > buffer && !visible) {
        setVisible(true);
      } else if (scrollTop < buffer && visible) {
        setVisible(false);
      }
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [visible]);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  if (onboardingStep == 0) {
    homePageContent = (
      <div className="px-4 sm:mx-6">
        <div className="text-center">
          <h1 className="mb-2 text-3xl font-bold text-gray-600">TextData</h1>
        </div>
        <Divider className="my-2" />

        {/* <div className="mb-4 flex flex-col lg:flex-row"> */}
        {/* Recently Accessed Submissions */}
        <div className="mb-4 lg:mb-0 lg:mx-60">
          <h2 className="text-xl font-semibold mb-4">Recently Accessed Submissions</h2>
          <QuickSubmissionBox className="mt-2" submissionData={recently_accessed_submissions} />
        </div>

        {/* Recommended Communities */}
        <div className="mb-4 lg:mb-0 lg:mx-60">
          <h2 className="text-xl font-semibold mb-4">Recommended Public Commmunities</h2>
          <RecommendedCommunityBox className="mt-2" recommendedCommunitiesData={recommendedCommunitiesData.recommended_communities} />
        </div>

        <Divider className="mb-4" />

        {/* Submission Graph */}
        {/*<div className="mb-8 lg:mx-60">
          <h2 className="text-xl font-semibold mb-4">Visualizing Your Submissions</h2>
          {!userOwnSubmissions ? (
            <div className="text-center">
              <Tooltip title="Loading" placement="top">
                <Skeleton animation="wave" variant="rectangular" width={'100ch'} height={300} />
              </Tooltip>
            </div>
          ) : (
            <div style={{ height: '65vh' }}>
              <HomeConnections nds={userOwnSubmissions && userOwnSubmissions['nodes']} eds={userOwnSubmissions && userOwnSubmissions['edges']} />
            </div>
          )}
        </div>*/}

        <Divider className="my-4" />

        <div className="mb-4 lg:mx-60">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">New Submissions</h2>
          </div>

          <InfiniteScroll
            dataLength={items.length}
            next={fetchNextPage}
            hasMore={!endOfRecommendations}
            loader={!endOfRecommendations && <div className="text-center">Loading...</div>}
            endMessage={endOfRecommendations && items.length > 0 ? <div className="text-center">You've reached the end of your recommendations.</div> : <div className="text-center">No recommendations to display. <br /> <a href="/community">Click here to create or join a community!</a></div>}
          >
            <div className="flex flex-col items-center">
              {items.map((d, idx) => (
                <div key={idx} className="mb-4 w-full">
                  <SearchResult
                    search_idx={idx}
                    redirect_url={d.redirect_url}
                    display_url={d.display_url}
                    submission_id={d.submission_id}
                    result_hash={d.result_hash}
                    description={d.description}
                    title={d.title}
                    time={d.time}
                    communities_part_of={d.communities_part_of}
                    auth_token={jsCookie.get("token")}
                    show_relevant={true}
                    hashtags={d.hashtags}
                    username={d.username}
                  />
                </div>
              ))}
            </div>
          </InfiniteScroll>
        </div >

        {
          visible && (
            <IconButton
              variant="extended"
              onClick={scrollToTop}
              sx={{
                width: '50px',
                height: '50px',
                ml: "auto",
                border: 'solid',
                bottom: '10px',
                position: 'fixed',
                right: '10px',
                backgroundColor: 'white',
                "&:hover": {
                  backgroundColor: "#1976d2",
                  color: 'white'
                }
              }}
            >
              <ArrowUpwardOutlined color="primary" />
            </IconButton>
          )
        }
      </div >
    );
  }

  return (
    <>
      <div className="allResults">

        <Head>
          <title>TextData</title>
          <link rel="icon" href="/images/tree32.png" />
        </Head>
        {homePageContent}
      </div>
    </>
  );
}

export async function getServerSideProps(context) {
  // Fetch data from external API
  if (
    context.req.cookies.token === "" ||
    context.req.cookies.token === undefined
  ) {
    return {
      redirect: {
        destination: "/about",
        permanent: false,
      },
    };
  } else {
    var recommendationURL = BASE_URL_SERVER + WEBSITE_SEARCH_ENDPOINT;
    recommendationURL += "?community=all";
    const res = await fetch(recommendationURL, {
      headers: new Headers({
        Authorization: context.req.cookies.token,
      }),
    });
    var recentlyAccessedSubmissionsURL = BASE_URL_SERVER + RECENTLY_ACCESSED_SUB_ENDPOINT;
    const recentlyAccessedSubmissions = await fetch(recentlyAccessedSubmissionsURL, {
      headers: new Headers({
        Authorization: context.req.cookies.token,
      }),
    });

    var communityURL = BASE_URL_SERVER + COMMUNITIES_ENDPOINT;
    const fetchCommunities = await fetch(communityURL, {
      headers: new Headers({
        Authorization: context.req.cookies.token,
      }),
    });


    const recommendedCommunities = await fetch(BASE_URL_SERVER + RECOMMEND_COMMUNITIES_ENDPOINT, {
      headers: new Headers({
        Authorization: context.req.cookies.token,
      }),
    });
    const recommendedCommunitiesData = await recommendedCommunities.json();

    var searchURL = BASE_URL_SERVER + WEBSITE_SEARCH_ENDPOINT;
    searchURL += "?own_submissions=True&community=all&visualize=True";

    const data = await res.json();
    const recently_accessed_submissions = await recentlyAccessedSubmissions.json();
    const community_joined_data = await fetchCommunities.json();
    if (fetchCommunities.status == 200) {
      if (res.status == 200) {
        if (recentlyAccessedSubmissions.status == 200) {
          if (context.query.page == undefined) {
            data.current_page = "0";
          } else {
            data.current_page = context.query.page;
          }
          return {
            props: {
              data, community_joined_data, recommendedCommunitiesData,
              recently_accessed_submissions
            }
          };
        }

      }
    } else if (fetchCommunities.status == 404) {
      return {
        redirect: {
          destination: "/auth",
          permanent: false,
        },
      };
    } else {
      const error_data = { error: "Something went wrong. Please try again later" };
      return { props: { error: { error_data } } };
    }
  }
}

export default Home;
