import { useState } from "react";
import Home from "./pages/Home";
import AnalysisWorkspace from "./pages/AnalysisWorkspace";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";

function App() {
  const [currentRoute, setCurrentRoute] = useState({ name: "home", props: {} });

  const navigateTo = (route, props = {}) => {
    setCurrentRoute({ name: route, props });
  };

  return (
    <>
      {currentRoute.name === "home" && <Home navigateTo={navigateTo} />}
      {currentRoute.name === "workspace" && (
        <AnalysisWorkspace
          navigateTo={navigateTo}
          initialConversationId={currentRoute.props.conversationId}
          initialLocationContext={currentRoute.props.locationContext}
        />
      )}
      {currentRoute.name === "login" && <Login navigateTo={navigateTo} />}
      {currentRoute.name === "signup" && <SignUp navigateTo={navigateTo} />}
    </>
  );
}

export default App;
