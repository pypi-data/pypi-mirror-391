import {Card, Group, Stack, Text,} from "@mantine/core";

import type {TrainingPhase} from "../models/trainingPhase.ts";

export const PhaseProgress = ({phase}: {phase: TrainingPhase}) => {
    return (
        <Card miw={600} mih={240} withBorder>
            <Card.Section bg="blue.2">
                <Group p={4} justify="space-between">
                    <Text fw={500}>Phase Progress</Text>
                </Group>
            </Card.Section>
            {phase ? <PhaseProgressContent phase={phase}/> : null}
        </Card>
    );
}

const PhaseProgressContent = ({phase}: {phase: TrainingPhase}) => {
    return (
        <Stack>
        </Stack>
    )
}
