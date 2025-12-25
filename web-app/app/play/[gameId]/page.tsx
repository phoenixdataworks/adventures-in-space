import GamePlayer from "./GamePlayer";

// Required for static export with dynamic routes
export function generateStaticParams() {
  return [
    { gameId: "adventures-in-space" },
    { gameId: "santa-vs-grunch" },
    { gameId: "snake-jump" },
    { gameId: "bible_stories" },
    { gameId: "joseph_mary_run" },
  ];
}

interface PageProps {
  params: Promise<{ gameId: string }>;
}

export default async function PlayPage({ params }: PageProps) {
  const { gameId } = await params;
  return <GamePlayer gameId={gameId} />;
}
