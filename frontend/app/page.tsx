
import AskQuestion from "@/components/questions/AskQuestion";
import { Toaster } from "sonner";

export default function Home() {

  return (
    <>
      <Toaster position="top-center"  />
      <AskQuestion />
    </>
  );
}
