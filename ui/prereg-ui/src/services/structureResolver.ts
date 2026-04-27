export function resolveStructure(input: any) {
  const {
    structureType,
    uniformWings,
    uniformFloors,
    floors,
    wings,
    baseFlats,
    flatsPerFloor,
  } = input;

  // ---------------- SCENARIO DETECTION ----------------

  let scenario = null;

  if (structureType === "SINGLE") {
    if (uniformFloors === true) scenario = "SCENARIO_1";
    if (uniformFloors === false) scenario = "SCENARIO_2";
  }

  if (structureType === "MULTI") {
    if (uniformWings === false) scenario = "SCENARIO_5";

    if (uniformWings === true && uniformFloors === true)
      scenario = "SCENARIO_3";

    if (uniformWings === true && uniformFloors === false)
      scenario = "SCENARIO_4";
  }

  if (!scenario) {
    return { error: "INCOMPLETE_INPUT" };
  }

  // ---------------- ROUTING ----------------

  if (scenario === "SCENARIO_5") {
    return {
      scenario,
      route: "/excel-upload-placeholder",
      mode: "EXCEL",
    };
  }

  if (scenario === "SCENARIO_2" || scenario === "SCENARIO_4") {
    return {
      scenario,
      route: "/structure-groups",
      mode: "GROUP",
      payload: {
        floors,
        wings,
        structureType,
      },
    };
  }

  // STANDARD
  return {
    scenario,
    route: "/structure-preview",
    mode: "STANDARD",
    payload: {
      floors,
      flatsPerFloor,
      baseFlats,
      wings:
        structureType === "SINGLE"
          ? [{ display_name: "Main", code: "A" }]
          : wings,
    },
  };
}